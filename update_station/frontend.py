import bectl
import datetime
import distro
import gettext
import json
import re
import sys
import threading
from gi.repository import Gtk, GLib
from subprocess import Popen, PIPE, run
from time import sleep
from update_station.common import update_progress
from update_station.data import Data
from update_station.dialog import FailedUpdate
from update_station.dialog import (
    MirrorSyncing,
    UpdateStationOpen,
    NoUpdateAvailable,
    ServerUnreachable,
    SomethingIsWrong,
    UpdateCompleted,
    RestartSystem
)
from update_station.backend import (
    check_for_update,
    get_packages_to_reinstall,
    get_pkg_upgrade_data,
    unlock_update_station,
    updating,
    look_update_station,
    repo_online,
    repository_is_syncing,
    network_stat
)

gettext.bindtextdomain('update-station', '/usr/local/share/locale')
gettext.textdomain('update-station')
_ = gettext.gettext

lib_path: str = f'{sys.prefix}/lib/update-station'


class UpdateWindow:
    """
    Class that creates the main window to see update list and start the update process.
    """
    def delete_event(self, widget: Gtk.Widget) -> None:
        """
        Function that handles the delete event when the window is closed.
        :param widget: The widget that triggered the delete event.
        """
        if Data.close_session is True:
            if updating():
                unlock_update_station()
            Gtk.main_quit()
        else:
            self.window.destroy()
            if Data.update_started is False:
                Data.stop_pkg_refreshing = False
                if updating():
                    unlock_update_station()
                Data.system_tray.tray_icon().set_visible(True)

    def start_update(self, widget):
        """
        Function that starts the update process.
        :param widget: The widget that triggered the start update event.
        """
        Data.update_started = True
        InstallUpdate()
        self.window.hide()

    def if_backup(self, widget):
        """
        Function that handles the backup checkbox.
        :param widget: The widget that triggered the checkbox event.
        """
        Data.backup = widget.get_active()

    def create_bbox(self):
        """
        Function that creates the button box.
        :return: The button box.
        """
        table = Gtk.Table(
            n_rows=1,
            n_columns=5,
            homogeneous=False,
            column_spacing=5
        )
        backup_checkbox = Gtk.CheckButton(
            label=_("Create boot environment backup")
        )
        table.attach(backup_checkbox, 0, 1, 0, 1)
        backup_checkbox.connect("toggled", self.if_backup)
        if bectl.is_file_system_zfs() and Data.second_update is False:
            backup_checkbox.set_active(True)
            backup_checkbox.set_sensitive(True)
            Data.backup = True
        else:
            backup_checkbox.set_active(False)
            backup_checkbox.set_sensitive(False)
            Data.backup = False
        img = Gtk.Image(icon_name='window-close')
        close_button = Gtk.Button(label=_("Close"))
        close_button.set_image(img)
        table.attach(close_button, 3, 4, 0, 1)
        close_button.connect("clicked", self.delete_event)
        install_button = Gtk.Button(label=_("Install update"))
        table.attach(install_button, 4, 5, 0, 1)
        install_button.connect("clicked", self.start_update)
        return table

    def __init__(self):
        """
        The constructor for the UpdateWindow class.
        """
        self.window = Gtk.Window()
        self.window.connect("destroy", self.delete_event)
        self.window.set_size_request(700, 400)
        self.window.set_resizable(False)
        self.window.set_title(_("Update Manager"))
        self.window.set_border_width(0)
        self.window.set_position(Gtk.WindowPosition.CENTER)
        self.window.set_default_icon_name('system-software-update')
        box1 = Gtk.VBox(homogeneous=False, spacing=0)
        self.window.add(box1)
        box1.show()
        box2 = Gtk.VBox(homogeneous=False, spacing=0)
        box2.set_border_width(20)
        box1.pack_start(box2, True, True, 0)
        box2.show()
        # Title
        title_text = _("Updates available!")

        update_title_label = Gtk.Label(
            label=f"<b><span size='large'>{title_text}</span></b>"
        )
        update_title_label.set_use_markup(True)
        box2.pack_start(update_title_label, False, False, 0)
        self.tree_store = Gtk.TreeStore(str, bool)
        sw = Gtk.ScrolledWindow()
        sw.set_shadow_type(Gtk.ShadowType.ETCHED_IN)
        sw.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        self.view = Gtk.TreeView(model=self.store())
        self.renderer = Gtk.CellRendererText()
        self.column0 = Gtk.TreeViewColumn("Name", self.renderer, text=0)
        self.view.append_column(self.column0)
        self.view.set_headers_visible(False)
        sw.add(self.view)
        sw.show()
        box2.pack_start(sw, True, True, 10)
        box2 = Gtk.HBox(homogeneous=False, spacing=10)
        box2.set_border_width(5)
        box1.pack_start(box2, False, False, 5)
        box2.show()
        # Add button
        box2.pack_start(self.create_bbox(), True, True, 10)
        self.window.show_all()

    def store(self):
        """
        Function that creates the store for the list of package in the treeview.
        :return: The store for the list of package to be updated.
        """
        self.tree_store.clear()
        r_num = 0
        u_num = 0
        i_num = 0
        ri_num = 0
        if bool(Data.packages_dictionary['remove']):
            r_num = len(Data.packages_dictionary['remove'])
            message = _('Installed packages to be REMOVED:')
            message += f' {r_num}'
            r_pinter = self.tree_store.append(None, (message, True))
            for line in Data.packages_dictionary['remove']:
                self.tree_store.append(r_pinter, (line, True))
        if bool(Data.packages_dictionary['upgrade']):
            u_num = len(Data.packages_dictionary['upgrade'])
            message = _('Installed packages to be UPGRADED')
            message += f' {u_num}'
            u_pinter = self.tree_store.append(None, (message, True))
            for line in Data.packages_dictionary['upgrade']:
                self.tree_store.append(u_pinter, (line, True))
        if bool(Data.packages_dictionary['install']):
            i_num = len(Data.packages_dictionary['install'])
            message = _('New packages to be INSTALLED:')
            message += f' {i_num}'
            i_pinter = self.tree_store.append(None, (message, True))
            for line in Data.packages_dictionary['install']:
                self.tree_store.append(i_pinter, (line, True))
        if bool(Data.packages_dictionary['reinstall']):
            ri_num = len(Data.packages_dictionary['reinstall'])
            message = _('Installed packages to be REINSTALLED:')
            message += f' {ri_num}'
            ri_pinter = self.tree_store.append(None, (message, True))
            for line in Data.packages_dictionary['reinstall']:
                self.tree_store.append(ri_pinter, (line, True))
        Data.total_packages = r_num + u_num + i_num + ri_num
        return self.tree_store

    def display(self, model: Gtk.TreeStore) -> Gtk.TreeView:
        """
        Function that creates the treeview.

        :param model: The store for the list of package to be updated.
        :return: The treeview.
        """
        self.view = Gtk.TreeView(model=model)
        self.renderer = Gtk.CellRendererText()
        self.column0 = Gtk.TreeViewColumn("Name", self.renderer, text=0)
        self.view.append_column(self.column0)
        self.view.set_headers_visible(False)
        return self.view


class InstallUpdate:
    """
    The class for the window that is displayed the progress of the update.
    """
    def close_application(self, widget):
        if updating():
            unlock_update_station()
        Gtk.main_quit()

    def __init__(self):
        """
        The constructor for the InstallUpdate class.
        """
        self.win = Gtk.Window()
        self.win.connect("delete-event", self.close_application)
        self.win.set_size_request(500, 75)
        self.win.set_resizable(False)
        self.win.set_title(_("Installing Update"))
        self.win.set_border_width(0)
        self.win.set_position(Gtk.WindowPosition.CENTER)
        self.win.set_default_icon_name('system-software-update')
        box1 = Gtk.VBox(homogeneous=False, spacing=0)
        self.win.add(box1)
        box1.show()
        box2 = Gtk.VBox(homogeneous=False, spacing=10)
        box2.set_border_width(10)
        box1.pack_start(box2, True, True, 0)
        box2.show()
        self.pbar = Gtk.ProgressBar()
        self.pbar.set_show_text(True)
        self.pbar.set_fraction(0.0)
        # self.pbar.set_size_request(-1, 20)
        box2.pack_start(self.pbar, False, False, 0)
        self.win.show_all()
        self.thr = threading.Thread(target=self.read_output, args=[self.pbar], daemon=True)
        self.thr.start()

    def read_output(self, progress):
        """
        Function that reads the output of the update to update the progress bar.
        :param progress: The progress bar.
        """
        fail = False
        update_pkg = False
        packages = ''
        env = f'env ABI={Data.new_abi} ' if Data.major_upgrade else ''
        need_reboot_packages = set(json.loads(open(f'{lib_path}/need_reboot.json').read()))
        upgrade_packages = set(re.findall(r"(\S+):", " ".join(Data.packages_dictionary['upgrade'])))
        reboot = bool(need_reboot_packages.intersection(upgrade_packages))
        if len(Data.packages_dictionary['upgrade']) == 1 and 'pkg:' in Data.packages_dictionary['upgrade'][0]:
            update_pkg = True
            packages = ' pkg'
            Data.second_update = True
        else:
            Data.second_update = False
        howmany = (Data.total_packages * 4) + 20
        fraction = 1.0 / howmany

        # TODO: make a function for this
        if Data.backup:
            today = datetime.datetime.now().strftime("%Y-%m-%d")
            txt = _("Cleaning old boot environment")
            GLib.idle_add(update_progress, progress, fraction, txt)
            for be in bectl.get_be_list():
                if 'backup' in be and today not in be and 'NR' not in be:
                    bectl.destroy_be(be.split()[0])
            backup_name = datetime.datetime.now().strftime(f"{distro.version()}-backup-%Y-%m-%d-%H-%M")
            txt = _("Creating boot environment")
            txt += f" {backup_name}"
            GLib.idle_add(update_progress, progress, fraction, txt)
            bectl.create_be(new_be_name=backup_name)
            sleep(1)

        if Data.major_upgrade:
            txt = _("Setting env and bootstrap pkg to upgrade")
            GLib.idle_add(update_progress, progress, fraction, txt)
            fetch = Popen(
                f'{env}env IGNORE_OSVERSION=yes ASSUME_ALWAYS_YES=yes pkg bootstrap -f',
                shell=True,
                stdout=PIPE,
                stderr=PIPE,
                close_fds=True,
                universal_newlines=True
            )
            fetch_text = ""
            while True:
                stdout_line = fetch.stdout.readline()
                if fetch.poll() is not None:
                    break
                fetch_text += stdout_line
                GLib.idle_add(update_progress, progress, fraction,
                              stdout_line.strip())
            if fetch.returncode != 0:
                stderr_line = fetch.stderr.read()
                fetch_text += stderr_line
                update_fail = open(f'{Data.home}/update.failed', 'w')
                update_fail.writelines(fetch_text)
                update_fail.close()
                fail = True
                GLib.idle_add(self.win.destroy)
                GLib.idle_add(self.stop_tread, fail, update_pkg, reboot)
                return
        txt = _("Downloading packages to upgrade")
        GLib.idle_add(update_progress, progress, fraction, txt)
        sleep(1)
        fetch = Popen(
            f'{env}pkg-static upgrade -Fy{packages}',
            shell=True,
            stdout=PIPE,
            stderr=PIPE,
            close_fds=True,
            universal_newlines=True
        )
        fetch_text = ""
        while True:
            stdout_line = fetch.stdout.readline()
            if fetch.poll() is not None:
                break
            fetch_text += stdout_line
            GLib.idle_add(update_progress, progress, fraction,
                          stdout_line.strip())
        if fetch.returncode != 0:
            stderr_line = fetch.stderr.read()
            fetch_text += stderr_line
            update_fail = open(f'{Data.home}/update.failed', 'w')
            update_fail.writelines(fetch_text)
            update_fail.close()
            fail = True
        else:
            txt = _("Packages to upgrade downloaded")
            GLib.idle_add(update_progress, progress, fraction, txt)
            sleep(1)
            txt = _("Upgrading packages")
            GLib.idle_add(update_progress, progress, fraction, txt)
            sleep(1)
            while True:
                install = Popen(
                    f'{env}pkg-static upgrade -y{packages}',
                    shell=True,
                    stdout=PIPE,
                    stderr=PIPE,
                    close_fds=True,
                    universal_newlines=True
                )
                install_text = ""
                while True:
                    stdout_line = install.stdout.readline()
                    if install.poll() is not None:
                        break
                    install_text += stdout_line
                    GLib.idle_add(update_progress, progress, fraction,
                                  stdout_line.strip())
                if install.returncode == 3:
                    stderr_line = install.stderr.readline()
                    if 'Fail to create temporary file' in stderr_line:
                        raw_line = install_text.splitlines()[-2]
                        failed_package = raw_line.split()[2].replace(':', '')
                        pkg_rquery = run(
                            f'{env}pkg-static rquery -x "%n" "{failed_package}"',
                            shell=True,
                            stdout=PIPE,
                            stderr=PIPE,
                            universal_newlines=True
                        )
                        package_name = pkg_rquery.stdout.strip()
                        reinstall = Popen(
                            f'{env}pkg-static delete -y {package_name} ;'
                            f'{env}pkg-static install -y {package_name}',
                            shell=True,
                            stdout=PIPE,
                            stderr=PIPE,
                            close_fds=True,
                            universal_newlines=True
                        )
                        reinstall_text = ""
                        while True:
                            stdout_line = reinstall.stdout.readline()
                            if reinstall.poll() is not None:
                                break
                            reinstall_text += stdout_line
                            GLib.idle_add(update_progress, progress,
                                          fraction, stdout_line.strip())
                        if reinstall.returncode != 0:
                            reinstall_text += reinstall.stderr.readline()
                            update_fail = open(f'{Data.home}/update.failed', 'w')
                            update_fail.writelines(reinstall_text)
                            update_fail.close()
                            fail = True
                            break
                        else:
                            txt = _("Reinstalling")
                            txt += f" {failed_package} "
                            txt += _("completed")
                            GLib.idle_add(update_progress, progress, fraction, txt)
                            sleep(1)
                elif install.returncode != 0:
                    stderr_line = install.stderr.readline()
                    install_text += stderr_line
                    update_fail = open(f'{Data.home}/update.failed', 'w')
                    update_fail.writelines(install_text)
                    update_fail.close()
                    fail = True
                    break
                else:
                    txt = _("Packages upgraded")
                    GLib.idle_add(update_progress, progress, fraction, txt)
                    sleep(1)
                    break
        if Data.kernel_upgrade:
            all_packages = set(re.findall(r"(\S+):", " ".join(Data.packages_dictionary['reinstall'])))
            all_packages.update(upgrade_packages)
            packages_to_reinstall = set(get_packages_to_reinstall())
            packages = " ".join(list(packages_to_reinstall.difference(all_packages)))
            txt = _("Downloading packages depending on kernel")
            GLib.idle_add(update_progress, progress, fraction, txt)
            sleep(1)
            fetch = Popen(
                f'{env}pkg-static upgrade -Fy {packages}',
                shell=True,
                stdout=PIPE,
                stderr=PIPE,
                close_fds=True,
                universal_newlines=True
            )
            fetch_text = ""
            while True:
                stdout_line = fetch.stdout.readline()
                if fetch.poll() is not None:
                    break
                fetch_text += stdout_line
                GLib.idle_add(update_progress, progress, fraction,
                              stdout_line.strip())
            if fetch.returncode != 0:
                stderr_line = fetch.stderr.read()
                fetch_text += stderr_line
                update_fail = open(f'{Data.home}/update.failed', 'w')
                update_fail.writelines(fetch_text)
                update_fail.close()
                fail = True
            else:
                txt = _("Packages depending on kernel downloaded")
                GLib.idle_add(update_progress, progress, fraction, txt)
                sleep(1)
                txt = _("Reinstalling packages depending on kernel")
                GLib.idle_add(update_progress, progress, fraction, txt)
                sleep(1)
                install = Popen(
                    f'{env}pkg-static upgrade -fy {packages}',
                    shell=True,
                    stdout=PIPE,
                    stderr=PIPE,
                    close_fds=True,
                    universal_newlines=True
                )
                install_text = ""
                while True:
                    stdout_line = install.stdout.readline()
                    if install.poll() is not None:
                        break
                    install_text += stdout_line
                    GLib.idle_add(update_progress, progress, fraction,
                                  stdout_line.strip())
                if install.returncode != 0:
                    stderr_line = install.stderr.readline()
                    install_text += stderr_line
                    update_fail = open(f'{Data.home}/update.failed', 'w')
                    update_fail.writelines(install_text)
                    update_fail.close()
                    fail = True
                else:
                    txt = _("Packages depending on kernel reinstalled")
                    GLib.idle_add(update_progress, progress, fraction, txt)
                    sleep(1)
        GLib.idle_add(self.win.destroy)
        GLib.idle_add(self.stop_tread, fail, update_pkg, reboot)

    @classmethod
    def stop_tread(cls, fail: bool, update_pkg: bool, reboot: bool):
        """
        The function to stop the thread.
        :param fail: True if update failed.
        :param update_pkg: True if update pkg was updated first.
        :param reboot: True if system needs to be rebooted after update completed.
        """
        if updating():
            unlock_update_station()
        if fail is True:
            Data.update_started = False
            Data.stop_pkg_refreshing = False
            FailedUpdate()
        else:
            if update_pkg is True and check_for_update() is True:
                Data.packages_dictionary = get_pkg_upgrade_data()
                StartCheckUpdate()
            else:
                Data.update_started = False
                Data.stop_pkg_refreshing = False
                if reboot is True:
                    RestartSystem()
                else:
                    UpdateCompleted()


class StartCheckUpdate:
    """
    Class for start check for update window.
    """
    def close_application(self, widget: Gtk.Widget):
        """
        The function to close the window.
        :param widget: The window widget.
        """
        if updating():
            unlock_update_station()
        Gtk.main_quit()

    def __init__(self):
        """
        The constructor of the StartCheckUpdate class.
        """
        self.win = Gtk.Window()
        self.win.connect("delete-event", self.close_application)
        self.win.set_size_request(500, 75)
        self.win.set_resizable(False)
        self.win.set_title(_("Looking For Updates"))
        self.win.set_border_width(0)
        self.win.set_position(Gtk.WindowPosition.CENTER)
        self.win.set_default_icon_name('system-software-update')
        box1 = Gtk.VBox(homogeneous=False, spacing=0)
        self.win.add(box1)
        box1.show()
        box2 = Gtk.VBox(homogeneous=False, spacing=10)
        box2.set_border_width(10)
        box1.pack_start(box2, True, True, 0)
        box2.show()
        self.pbar = Gtk.ProgressBar()
        self.pbar.set_show_text(True)
        self.pbar.set_fraction(0.0)
        box2.pack_start(self.pbar, False, False, 0)
        self.win.show_all()
        self.thr = threading.Thread(
            target=self.check_for_update,
            args=[self.pbar],
            daemon=True
        )
        self.thr.start()

    def update_progress(self, progress: Gtk.ProgressBar, text: str):
        """
        The function to update the progress bar.
        :param progress: The progress bar.
        :param text: the text to be displayed on the progress bar.
        """
        progress.set_text(text)
        fraction = progress.get_fraction() + 0.2
        progress.set_fraction(fraction)

    def check_for_update(self, progress: Gtk.ProgressBar):
        """
        The function to check for update and update the progress bar.
        :param progress: The progress bar.
        """
        GLib.idle_add(self.update_progress, progress,
                      _('Checking if the repository is online'))
        sleep(1)
        if network_stat() == 'UP' and repo_online() is True:
            GLib.idle_add(self.update_progress, progress,
                          _('The repository is online'))
            sleep(1)
            if repository_is_syncing() is True:
                GLib.idle_add(self.update_progress, progress,
                              _('The mirror is Syncing'))
                GLib.idle_add(self.stop_tread, MirrorSyncing)
            else:
                if updating():
                    GLib.idle_add(self.update_progress, progress,
                                  _('Updates are already running'))
                    GLib.idle_add(self.stop_tread, UpdateStationOpen)
                else:
                    GLib.idle_add(self.update_progress, progress,
                                  _('Checking for updates'))
                    update_available = check_for_update()
                    if update_available:
                        GLib.idle_add(self.update_progress, progress,
                                      _('Getting the list of packages'))
                        Data.packages_dictionary = get_pkg_upgrade_data()
                        look_update_station()
                        GLib.idle_add(self.update_progress, progress,
                                      _('Open the update window'))
                        GLib.idle_add(self.stop_tread, UpdateWindow)
                    elif not update_available and update_available is not None:
                        GLib.idle_add(self.update_progress, progress,
                                      _('No update found'))
                        GLib.idle_add(self.stop_tread, NoUpdateAvailable)
                    else:
                        GLib.idle_add(self.stop_tread, SomethingIsWrong)
        else:
            GLib.idle_add(self.update_progress, progress,
                          _('The Mirror is unreachable'))
            GLib.idle_add(self.stop_tread, ServerUnreachable)

    def stop_tread(self, start_window: object):
        """
        The function to stop the thread.
        :param start_window: The start window object.
        """
        start_window()
        self.win.hide()
