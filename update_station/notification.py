import gettext

from gi.repository import Gtk, GLib, Notify
from update_station.data import Data
from update_station.backend import updating
from update_station.frontend import StartCheckUpdate
from update_station.dialog import UpdateStationOpen

gettext.bindtextdomain('update-station', '/usr/local/share/locale')
gettext.textdomain('update-station')
_ = gettext.gettext


class UpdateNotifier:
    """
    Class that creates the notification for the update.
    """

    def __init__(self):
        """
        The constructor for the UpdateNotifier class.
        """
        self.notification = None
        Notify.init('Test')
        self.msg = _("Software updates are now available.")
        self.timeout = 10000  # 10 seconds

    def notify(self):
        """
        Function that creates the notification for the update.
        """
        if Data.major_upgrade is True:
            self.msg = _("Major system version upgrade is now available.")
        elif Data.kernel_upgrade is True:
            self.msg = _("System and software updates are now available.")
        self.notification = Notify.Notification().new(
            summary=_('Update Available'),
            body=self.msg,
            icon='system-software-update'
        )
        self.notification.add_action('clicked', 'Start Upgrade', self.on_activated)
        self.notification.show()

    def on_activated(self, notification, action_name):
        """
        Function that starts the upgrade.
        :param notification: The notification widget.
        :param action_name: The name of the action.
        """
        if Data.major_upgrade is True:
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
        self.status_icon.set_tooltip_text('Update Available')
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
            if Data.major_upgrade is True:
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
        self.connect("destroy", Gtk.main_quit)
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        vbox.set_border_width(10)
        self.add(vbox)

        label = Gtk.Label(
            label=_(f"Would you like to upgrade from {Data.current_abi} to {Data.new_abi}?"
                    "\n\nIf you select No, the upgrade will be skipped until the next boot.")
        )
        vbox.pack_start(label, True, True, 5)
        hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
        vbox.pack_start(hbox, False, False, 0)
        button1 = Gtk.Button(label="Yes")
        button1.connect("clicked", self.on_clicked)
        hbox.pack_end(button1, True, True, 0)

        button2 = Gtk.Button(label="No")
        button2.connect("clicked", self.on_clicked)
        hbox.pack_end(button2, True, True, 0)
        self.show_all()

    def on_clicked(self, widget):
        """
        Function that starts the upgrade.
        :param widget: The widget that was clicked.
        """
        if widget.get_label() == "Yes":
            Data.major_upgrade = True
            Data.do_not_upgrade = False
            StartCheckUpdate()
        else:
            Data.major_upgrade = False
            Data.do_not_upgrade = True
        self.destroy()
