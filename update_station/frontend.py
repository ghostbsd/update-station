import bectl
import datetime
import distro
import gettext
import json
import re
import sys
import threading
from gi.repository import Gtk, GLib, Notify
from time import sleep
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
    get_pkg_upgrade_data,
    unlock_update_station,
    updating,
    look_update_station,
    repo_online,
    repository_is_syncing,
    network_stat,
    command_output,
    is_major_upgrade_available,
    get_current_abi,
    get_abi_upgrade
)

gettext.bindtextdomain('update-station', '/usr/local/share/locale')
gettext.textdomain('update-station')
_ = gettext.gettext

lib_path: str = f'{sys.prefix}/lib/update-station'


def update_progress(progress: Gtk.ProgressBar, fraction: float, text: str) -> None:
    """
    Update the progress bar with new fraction and text.

    :param progress: The progress bar.
    :param fraction: The fraction to add.
    :param text: The text to display.
    """
    new_val = progress.get_fraction() + fraction
    progress.set_fraction(new_val)
    progress.set_text(text)


class UpdateWindow:
    """
    Class that creates the main window to see update list and start the update process.
    """
    def delete_event(self, _widget: Gtk.Widget, _event=None) -> None:
        """
        Function that handles the delete event when the window is closed.

        :param _widget: The widget that triggered the delete event.
        :param _event: The event that triggered the delete event.
        """
        if Data.close_session:
            if updating():
                unlock_update_station()
            Gtk.main_quit()
        else:
            self.window.destroy()
            if not Data.update_started:
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
        self.window.destroy()

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
        self.window.connect("delete-event", self.delete_event)
        self.window.set_size_request(700, 400)
        self.window.set_resizable(False)
        self.window.set_title(_("Update Manager"))
        self.window.set_border_width(0)
        self.window.set_position(Gtk.WindowPosition.CENTER)
        self.window.set_default_icon_name('system-software-update')
        vbox1 = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, homogeneous=False, spacing=0)
        self.window.add(vbox1)
        vbox1.show()
        vbox2 = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, homogeneous=False, spacing=0)
        vbox2.set_border_width(20)
        vbox1.pack_start(vbox2, True, True, 0)
        vbox2.show()
        # Title
        title_text = _("Updates available!")

        update_title_label = Gtk.Label(
            label=f"<b><span size='large'>{title_text}</span></b>"
        )
        update_title_label.set_use_markup(True)
        vbox2.pack_start(update_title_label, False, False, 0)
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
        vbox2.pack_start(sw, True, True, 10)
        hbox2 = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, homogeneous=False, spacing=10)
        hbox2.set_border_width(5)
        vbox1.pack_start(hbox2, False, False, 5)
        hbox2.show()
        # Add button
        hbox2.pack_start(self.create_bbox(), True, True, 10)
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
        if Data.packages_dictionary['upgrade']:
            message = _('Installed packages to be upgraded:')
            message += f' {Data.packages_dictionary["number_to_upgrade"]}'
            u_pinter = self.tree_store.append(None, (message, True))
            for line in Data.packages_dictionary['upgrade']:
                self.tree_store.append(u_pinter, (line, True))
        if Data.packages_dictionary['downgrade']:
            message = _('Installed packages to be downgraded:')
            message += f' {Data.packages_dictionary["number_to_downgrade"]}'
            d_pinter = self.tree_store.append(None, (message, True))
            for line in Data.packages_dictionary['downgrade']:
                self.tree_store.append(d_pinter, (line, True))
        if bool(Data.packages_dictionary['install']):
            message = _('New packages to be installed:')
            message += f' {Data.packages_dictionary["number_to_install"]}'
            i_pinter = self.tree_store.append(None, (message, True))
            for line in Data.packages_dictionary['install']:
                self.tree_store.append(i_pinter, (line, True))
        if bool(Data.packages_dictionary['reinstall']):
            message = _('Installed packages to be reinstalled:')
            message += f' {Data.packages_dictionary["number_to_reinstall"]}'
            ri_pinter = self.tree_store.append(None, (message, True))
            for line in Data.packages_dictionary['reinstall']:
                self.tree_store.append(ri_pinter, (line, True))
        if bool(Data.packages_dictionary['remove']):
            message = _('Installed packages to be removed:')
            message += f' {Data.packages_dictionary["number_to_remove"]}'
            r_pinter = self.tree_store.append(None, (message, True))
            for line in Data.packages_dictionary['remove']:
                self.tree_store.append(r_pinter, (line, True))
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
        vbox1 = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, homogeneous=False, spacing=0)
        self.win.add(vbox1)
        vbox1.show()
        vbox2 = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, homogeneous=False, spacing=10)
        vbox2.set_border_width(10)
        vbox1.pack_start(vbox2, True, True, 0)
        vbox2.show()
        self.pbar = Gtk.ProgressBar()
        self.pbar.set_show_text(True)
        self.pbar.set_fraction(0.0)
        # self.pbar.set_size_request(-1, 20)
        vbox2.pack_start(self.pbar, False, False, 0)
        self.win.show_all()
        self.thr = threading.Thread(target=self.read_output, args=[self.pbar], daemon=True)
        self.thr.start()

    @classmethod
    def should_destroy_be(cls, be_line: str, today_str: str) -> bool:
        """
        Determines if a Boot Environment should be destroyed based on criteria.
        Returns False if the BE is protected (active and mounted at root).
        :param be_line: The BE line to check.
        :param today_str:  The string representation of today's date.
        :return: True if the BE should be destroyed, False otherwise.
        """
        # Split the line into columns, handling multiple spaces
        columns = be_line.split()
        if len(columns) < 4:
            return False

        be_name = columns[0]
        active_status = columns[1]
        mount_point = columns[2]

        # Protect BE if it's active (N) AND mounted at root (/)
        if 'N' in active_status and mount_point == '/':
            return False

        if 'R' in active_status:
            return False

        # Apply your original deletion criteria
        return (
                'backup' in be_name and
                today_str not in be_name and
                'NR' not in active_status
        )

    @classmethod
    def log_failure(cls, text: str) -> None:
        """
        Write update failure details to a file.

        :param text: The failure text to write.
        """
        with open(f'{Data.home}/update.failed', 'w') as f:
            f.writelines(text)

    @classmethod
    def process_output(
        cls, command: str, progress: Gtk.ProgressBar, fraction: float
    ) -> tuple:
        """
        Run a command and read its stdout line by line, updating the progress bar.

        :param command: The shell command to run.
        :param progress: The progress bar.
        :param fraction: The fraction to increment the progress bar.
        :return: A tuple of (returncode, stdout_text, stderr_text).
        """
        proc = command_output(command)
        stdout_text = ""
        while True:
            line = proc.stdout.readline()
            if not line:
                break
            stdout_text += line
            GLib.idle_add(update_progress, progress, fraction, line.strip())
        proc.wait()
        stderr_text = proc.stderr.read()
        return proc.returncode, stdout_text, stderr_text

    @classmethod
    def needs_reboot(cls) -> bool:
        """
        Check if any packages being upgraded require a system reboot.

        :return: True if a reboot is needed, False otherwise.
        """
        with open(f'{lib_path}/need_reboot.json') as f:
            need_reboot_packages = set(json.loads(f.read()))
        upgrade_packages = set(re.split(": | ", " ".join(Data.packages_dictionary['upgrade'])))
        return bool(need_reboot_packages.intersection(upgrade_packages))

    @classmethod
    def is_pkg_only_update(cls) -> tuple:
        """
        Check if only the pkg package itself is being updated.

        :return: A tuple of (update_pkg, packages) where update_pkg is True
                 if only pkg is being updated and packages is the package string.
        """
        if len(Data.packages_dictionary['upgrade']) == 1 and 'pkg:' in Data.packages_dictionary['upgrade'][0]:
            Data.second_update = True
            return True, ' pkg'
        Data.second_update = False
        return False, ''

    def install_packages(self, env: str, option: str, packages: str, progress: Gtk.ProgressBar, fraction: float) -> bool:
        """
        Install package updates with retry logic for temporary file failures.

        :param env: The ABI environment prefix.
        :param option: The upgrade option flag.
        :param packages: The package names to install.
        :param progress: The progress bar.
        :param fraction: The fraction to increment the progress bar.
        :return: True if install succeeded, False otherwise.
        """
        progress_message = _("Package updates downloaded")
        GLib.idle_add(update_progress, progress, fraction, progress_message)
        sleep(1)
        progress_message = _("Installing package updates")
        GLib.idle_add(update_progress, progress, fraction, progress_message)
        sleep(1)
        packages_to_reinstall = []
        max_retries = 5
        for retry in range(max_retries):
            return_code, install_text, stderr_text = self.process_output(
                f'{env}pkg-static upgrade -y{option}{packages}',
                progress, fraction
            )
            if return_code == 3 and 'Fail to create temporary file' in stderr_text:
                raw_line = install_text.splitlines()[-2]
                failed_package = raw_line.split()[2].replace(':', '')
                rquery = command_output(
                    f'{env}pkg-static rquery -x "%n" "{failed_package}"'
                )
                package_name = rquery.stdout.read().strip()
                return_code, delete_text, stderr_text = self.process_output(
                    f'{env}pkg-static delete -y {package_name}',
                    progress, fraction
                )
                if return_code != 0:
                    self.log_failure(delete_text + stderr_text)
                    break
                packages_to_reinstall.append(package_name)
                progress_message = _("Removed")
                progress_message += f" {failed_package}, "
                progress_message += _("will reinstall after upgrade")
                GLib.idle_add(update_progress, progress, fraction, progress_message)
                sleep(1)
            elif return_code != 0:
                self.log_failure(install_text + stderr_text)
                break
            else:
                progress_message = _("Software packages upgrade completed")
                GLib.idle_add(update_progress, progress, fraction, progress_message)
                sleep(1)
                break
        else:
            self.log_failure(install_text + stderr_text)
            return False
        for package_name in packages_to_reinstall:
            progress_message = _("Reinstalling") + f" {package_name}"
            GLib.idle_add(update_progress, progress, fraction, progress_message)
            return_code, reinstall_text, stderr_text = self.process_output(
                f'{env}pkg-static install -y {package_name}',
                progress, fraction
            )
            if return_code != 0:
                self.log_failure(reinstall_text + stderr_text)
                return False
        return return_code == 0

    def fetch_packages(self, env: str, option: str, packages: str, progress: Gtk.ProgressBar, fraction: float) -> bool:
        """
        Fetch package updates.

        :param env: The ABI environment prefix.
        :param option: The upgrade option flag.
        :param packages: The package names to fetch.
        :param progress: The progress bar.
        :param fraction: The fraction to increment the progress bar.
        :return: True if fetch succeeded, False otherwise.
        """
        progress_message = _("Fetching package updates")
        GLib.idle_add(update_progress, progress, fraction, progress_message)
        sleep(1)
        return_code, stdout_text, stderr_text = self.process_output(
            f'{env}pkg-static upgrade -Fy{option}{packages}',
            progress, fraction
        )
        if return_code != 0:
            self.log_failure(stdout_text + stderr_text)
            return False
        return True

    def bootstrap_major_upgrade(self, env: str, progress: Gtk.ProgressBar, fraction: float) -> bool:
        """
        Bootstrap pkg for a major version upgrade.

        :param env: The ABI environment prefix.
        :param progress: The progress bar.
        :param fraction: The fraction to increment the progress bar.
        :return: True if bootstrap succeeded, False otherwise.
        """
        progress_message = _("Fetching package updates")
        GLib.idle_add(update_progress, progress, fraction, progress_message)
        return_code, stdout_text, stderr_text = self.process_output(
            f'{env}env IGNORE_OSVERSION=yes ASSUME_ALWAYS_YES=yes pkg bootstrap -f',
            progress, fraction
        )
        if return_code != 0:
            self.log_failure(stdout_text + stderr_text)
            return False
        return True

    def prepare_backup(self, progress: Gtk.ProgressBar, fraction: float) -> None:
        """
        Clean old boot environments and create a new backup.

        :param progress: The progress bar.
        :param fraction: The fraction to increment the progress bar.
        """
        today = datetime.datetime.now().strftime("%Y-%m-%d")
        progress_message = _("Cleaning old boot environment")
        GLib.idle_add(update_progress, progress, fraction, progress_message)
        for be in bectl.get_be_list():
            if self.should_destroy_be(be, today):
                bectl.destroy_be(be.split()[0])
        backup_name = datetime.datetime.now().strftime(
            f"{distro.version()}-backup-%Y-%m-%d-%H-%M"
        )
        progress_message = _("Creating boot environment")
        progress_message += f" {backup_name}"
        GLib.idle_add(update_progress, progress, fraction, progress_message)
        bectl.create_be(new_be_name=backup_name)
        sleep(1)

    def read_output(self, progress):
        """
        Function that reads the output of the update to update the progress bar.
        :param progress: The progress bar.
        """
        fail = False
        env = f'env ABI={Data.new_abi} ' if Data.major_upgrade else ''
        reboot = self.needs_reboot()
        update_pkg, packages = self.is_pkg_only_update()
        option = 'f' if Data.kernel_upgrade else ''
        howmany = (Data.packages_dictionary['total_of_packages'] * 7) + 45
        fraction = 1.0 / howmany
        if Data.backup:
            self.prepare_backup(progress, fraction)
        if Data.major_upgrade and not self.bootstrap_major_upgrade(env, progress, fraction):
            GLib.idle_add(self.win.destroy)
            GLib.idle_add(self.stop_tread, True, update_pkg, reboot)
            return
        if not self.fetch_packages(env, option, packages, progress, fraction):
            fail = True
        elif not self.install_packages(env, option, packages, progress, fraction):
            fail = True
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
        if fail:
            Data.update_started = False
            Data.stop_pkg_refreshing = False
            FailedUpdate()
        elif update_pkg and check_for_update() is True:
            Data.packages_dictionary = get_pkg_upgrade_data()
            StartCheckUpdate()
        else:
            Data.update_started = False
            Data.stop_pkg_refreshing = False
            if reboot:
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
        vbox1 = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, homogeneous=False, spacing=0)
        self.win.add(vbox1)
        vbox1.show()
        vbox2 = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, homogeneous=False, spacing=10)
        vbox2.set_border_width(10)
        vbox1.pack_start(vbox2, True, True, 0)
        vbox2.show()
        self.pbar = Gtk.ProgressBar()
        self.pbar.set_show_text(True)
        self.pbar.set_fraction(0.0)
        vbox2.pack_start(self.pbar, False, False, 0)
        self.win.show_all()
        self.thr = threading.Thread(
            target=self.check_for_update,
            args=[self.pbar],
            daemon=True
        )
        self.thr.start()

    @classmethod
    def update_progress(cls, progress: Gtk.ProgressBar, text: str):
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
            if repository_is_syncing():
                GLib.idle_add(self.update_progress, progress,
                              _('The mirror is Syncing'))
                GLib.idle_add(self.stop_tread, MirrorSyncing)
            elif updating():
                GLib.idle_add(self.update_progress, progress,
                              _('Updates are already running'))
                GLib.idle_add(self.stop_tread, UpdateStationOpen)
            else:
                GLib.idle_add(self.update_progress, progress,
                              _('Checking for updates'))
                if update_available := check_for_update():
                    GLib.idle_add(self.update_progress, progress,
                                  _('Getting the list of packages'))
                    Data.packages_dictionary = get_pkg_upgrade_data()
                    look_update_station()
                    GLib.idle_add(self.update_progress, progress,
                                  _('Open the update window'))
                    GLib.idle_add(self.stop_tread, UpdateWindow)
                elif update_available is not None:
                    # No regular updates, check for major upgrade
                    if is_major_upgrade_available() and Data.do_not_upgrade is False:
                        Data.major_upgrade = True
                        Data.current_abi = get_current_abi()
                        Data.new_abi = get_abi_upgrade()
                        GLib.idle_add(self.stop_tread, MajorUpgradeWindow)
                    else:
                        GLib.idle_add(self.update_progress, progress,
                                      _('No update found'))
                        GLib.idle_add(self.stop_tread, NoUpdateAvailable)
                else:
                    GLib.idle_add(self.stop_tread, SomethingIsWrong)

        else:
            GLib.idle_add(self.update_progress, progress,
                          _('The Mirror is unreachable'))
            GLib.idle_add(self.stop_tread, ServerUnreachable)

    def stop_tread(self, start_window):
        """
        The function to stop the thread.
        :param start_window: The start window object.
        """
        self.win.destroy()
        start_window()


class UpdateNotifier:
    """
    Class that creates the notification for the update.
    """

    def __init__(self):
        """
        The constructor for the UpdateNotifier class.
        """
        self.notification = None
        # Only initialize once
        if not Notify.is_initted():
            Notify.init('update-station')
        self.msg = _("Software updates are now available.")
        self.timeout = 10000  # 10 seconds

    def notify(self):
        """
        Function that creates the notification for the update.
        """
        if Data.major_upgrade:
            self.msg = _("Major system version upgrade is now available.")
        elif Data.kernel_upgrade:
            self.msg = _("System and software updates are now available.")
        self.notification = Notify.Notification().new(
            summary=_('Update Available'),
            body=self.msg,
            icon='system-software-update'
        )
        self.notification.add_action('clicked', 'Start Upgrade', self.on_activated)
        self.notification.show()

    def on_activated(self, notification, _action_name):
        """
        Function that starts the upgrade.
        :param notification: The notification widget.
        :param _action_name: The name of the action.
        """
        if Data.major_upgrade:
            MajorUpgradeWindow()
        else:
            StartCheckUpdate()
        notification.close()
        GLib.idle_add(Data.system_tray.tray_icon().set_visible, False)


class TrayIcon:
    """
    The class for the tray icon.
    """

    def tray_icon(self):
        return self.status_icon

    def __init__(self):
        """
        The constructor for the TrayIcon class.
        """
        self.status_icon = Gtk.StatusIcon()
        self.status_icon.set_tooltip_text(_('Update Available'))
        self.menu = Gtk.Menu()
        self.menu.show_all()
        self.status_icon.connect("activate", self.left_click)
        self.status_icon.connect('popup-menu', self.icon_clicked)
        self.status_icon.set_visible(False)
        self.status_icon.set_from_icon_name('system-software-update')

    def nm_menu(self):
        """
        Function that creates the menu for the tray icon.
        :return: The menu.
        """
        self.menu = Gtk.Menu()
        open_update = Gtk.MenuItem(label=_("Open Update"))
        open_update.connect("activate", self.left_click)
        close_item = Gtk.MenuItem(label=_("Close"))
        close_item.connect("activate", Gtk.main_quit)
        self.menu.append(open_update)
        self.menu.append(close_item)
        self.menu.show_all()
        return self.menu

    @classmethod
    def left_click(cls, status_icon: Gtk.StatusIcon):
        """
        Function that is called when the user left-clicks on the tray icon.
        :param status_icon: The status icon.
        """
        if updating():
            UpdateStationOpen()
        else:
            Data.stop_pkg_refreshing = True
            if Data.major_upgrade:
                MajorUpgradeWindow()
            else:
                StartCheckUpdate()
        status_icon.set_visible(False)

    def icon_clicked(self, status_icon, button, time):
        """
        Function that is called when the user right-clicks on the tray icon.
        :param status_icon: The status icon.
        :param button: The button.
        :param time: The time.
        """
        position = Gtk.StatusIcon.position_menu
        self.nm_menu().popup(None, None, position, status_icon, button, time)


class MajorUpgradeWindow(Gtk.Window):
    """
    Class that creates the window for the major upgrade.
    """

    def __init__(self):
        """
        The constructor for the MajorUpgradeWindow class.
        """
        Gtk.Window.__init__(self, title=_("Major version upgrade"))
        self.connect("delete-event", self.on_close)
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        vbox.set_border_width(10)
        self.add(vbox)

        label = Gtk.Label(
            label=_(
                "Would you like to upgrade from {current} to {new}?\n\n"
                "If you select No, the upgrade will be skipped until the next boot."
            ).format(current=Data.current_abi, new=Data.new_abi)
        )
        vbox.pack_start(label, True, True, 5)
        hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
        vbox.pack_start(hbox, False, False, 0)
        button1 = Gtk.Button(label=_("Yes"))
        button1.connect("clicked", self.on_yes_clicked)
        hbox.pack_end(button1, True, True, 0)

        button2 = Gtk.Button(label=_("No"))
        button2.connect("clicked", self.on_no_clicked)
        hbox.pack_end(button2, True, True, 0)
        self.show_all()

    def on_yes_clicked(self, _widget):
        """
        Function that starts the upgrade when Yes is clicked.
        :param _widget: The widget that was clicked.
        """
        Data.major_upgrade = True
        Data.do_not_upgrade = False
        StartCheckUpdate()
        self.destroy()

    def on_no_clicked(self, _widget):
        """
        Function that declines the upgrade when No is clicked.
        :param _widget: The widget that was clicked.
        """
        Data.major_upgrade = False
        Data.do_not_upgrade = True
        self.destroy()

    def on_close(self, _widget: Gtk.Widget, _event=None) -> bool:
        """
        Handle window close event.

        :param _widget: The widget that triggered the event.
        :param _event: The event object.
        :return: True to prevent default GTK behavior.
        """
        if Data.close_session:
            Gtk.main_quit()
        else:
            self.destroy()
        return True
