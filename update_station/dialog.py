#!/usr/local/bin/python

import gi
import gettext
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
from update_station.common import on_close
from update_station.backend import (
    get_detail,
    on_reboot
)

gettext.bindtextdomain('update-station', '/usr/local/share/locale')
gettext.textdomain('update-station')
_ = gettext.gettext


class FailedUpdate:
    """
    FailedUpdate class for failed update window.
    """

    def __init__(self):
        """
        The constructor of the FailedUpdate class.
        """
        window = Gtk.Window()
        window.set_position(Gtk.WindowPosition.CENTER)
        # self.window.set_border_width(8)
        window.connect("delete-event", on_close, window)
        window.set_title(_("Update Failed"))
        window.set_default_icon_name('system-software-update')
        v_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, homogeneous=False, spacing=0)
        window.add(v_box)
        v_box.show()
        label = Gtk.Label()
        failed_text = _("""Press "Detail" to get information about the failure.
        Get help at https://forums.ghostbsd.org or .""")
        label.set_markup(failed_text)
        v_box.set_border_width(5)
        v_box.pack_start(label, False, False, 5)
        h_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, homogeneous=False, spacing=0)
        # hBox.set_border_width(5)
        v_box.pack_start(h_box, False, True, 5)
        h_box.show()
        restart = Gtk.Button(label=_("Detail"))
        restart.connect("clicked", get_detail)
        continue_button = Gtk.Button(label=_("Close"))
        continue_button.connect("clicked", on_close, window)
        h_box.pack_end(continue_button, False, False, 5)
        h_box.pack_end(restart, False, False, 5)
        window.show_all()


class RestartSystem:
    """
    RestartSystem class for restarting system window.
    """

    def __init__(self):
        """
        The constructor of the RestartSystem class.
        """
        window = Gtk.Window()
        window.set_position(Gtk.WindowPosition.CENTER)
        # self.window.set_border_width(8)
        window.connect("destroy", on_close, window)
        window.set_title(_("Update Completed"))
        window.set_default_icon_name('system-software-update')
        v_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, homogeneous=False, spacing=0)
        window.add(v_box)
        v_box.show()
        reboot_text = _("The computer needs to restart to run on the updated software.")
        label = Gtk.Label(label=reboot_text)
        v_box.set_border_width(5)
        v_box.pack_start(label, False, False, 5)
        h_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, homogeneous=False, spacing=0)
        # h_box.set_border_width(5)
        v_box.pack_start(h_box, False, True, 5)
        h_box.show()
        restart = Gtk.Button(label=_("Restart Now"))
        restart.connect("clicked", on_reboot)
        continue_button = Gtk.Button(label=_("Restart Later"))
        continue_button.connect("clicked", on_close, window)
        h_box.pack_end(restart, False, False, 5)
        h_box.pack_end(continue_button, False, False, 5)
        window.show_all()


class UpdateCompleted:
    """
    Class for update completed window.
    """

    def __init__(self):
        """
        The constructor of the UpdateCompleted class.
        """
        window = Gtk.Window()
        window.set_position(Gtk.WindowPosition.CENTER)
        window.connect("destroy", on_close, window)
        window.set_title(_("Update Completed"))
        window.set_default_icon_name('system-software-update')
        v_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, hhomogeneous=False, spacing=0)
        window.add(v_box)
        v_box.show()
        label = Gtk.Label(label=_("""All software on this system is up to date."""))
        v_box.set_border_width(5)
        v_box.pack_start(label, False, False, 5)
        h_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, hhomogeneous=False, spacing=0)
        # h_box.set_border_width(5)
        v_box.pack_start(h_box, False, True, 5)
        h_box.show()
        close_button = Gtk.Button(label=_("Close"))
        close_button.connect("clicked", on_close, window)
        h_box.pack_end(close_button, False, False, 5)
        window.show_all()


class NoUpdateAvailable(object):
    """
    Class for no update available window.
    """

    def __init__(self):
        """
        The constructor of the NoUpdateAvailable class.
        """
        window = Gtk.Window()
        window.set_position(Gtk.WindowPosition.CENTER)
        window.set_border_width(8)
        window.connect("destroy", on_close, window)
        window.set_title(_("No Update Available"))
        vbox1 = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, homogeneous=False, spacing=0)
        window.add(vbox1)
        vbox1.show()
        vbox2 = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, homogeneous=False, spacing=10)
        vbox2.set_border_width(10)
        vbox1.pack_start(vbox2, True, True, 0)
        vbox2.show()
        label = Gtk.Label(label=_("No update available. This system is up "
                          "to date."))
        vbox2.pack_start(label, False, False, 0)
        hbox1 = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, homogeneous=False, spacing=10)
        hbox1.set_border_width(5)
        vbox1.pack_start(hbox1, False, True, 0)
        hbox1.show()
        ok_button = Gtk.Button(label=_("Close"))
        ok_button.connect("clicked", on_close, window)
        hbox1.pack_end(ok_button, False, False, 0)
        window.show_all()


class UpdateStationOpen(object):
    """
    Class for update station already started window.
    """

    def __init__(self):
        """
        The constructor of the UpdateStationOpen class.
        """
        window = Gtk.Window()
        window.set_position(Gtk.WindowPosition.CENTER)
        window.set_border_width(8)
        window.connect("destroy", on_close, window)
        window.set_title(_("Update Station already started"))
        vbox1 = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, homogeneous=False, spacing=0)
        window.add(vbox1)
        vbox1.show()
        vbox2 = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, homogeneous=False, spacing=10)
        vbox2.set_border_width(10)
        vbox1.pack_start(vbox2, True, True, 0)
        vbox2.show()
        label = Gtk.Label(label=_("Update Station already open."))
        vbox2.pack_start(label, False, False, 0)
        hbox2 = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, homogeneous=False, spacing=10)
        hbox2.set_border_width(5)
        vbox1.pack_start(hbox2, False, True, 0)
        hbox2.show()
        ok_button = Gtk.Button(label=_("Close"))
        ok_button.connect("clicked", on_close, window)
        hbox2.pack_end(ok_button, False, False, 0)
        window.show_all()


class MirrorSyncing(object):
    """
    Class for the mirror is syncing warning window.
    """

    def __init__(self):
        """
        The constructor of the MirrorSyncing class.
        """
        window = Gtk.Window()
        window.set_position(Gtk.WindowPosition.CENTER)
        window.set_border_width(8)
        window.connect("destroy", on_close, window)
        window.set_title(_("Server Unreachable"))
        vbox1 = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, homogeneous=False, spacing=0)
        window.add(vbox1)
        vbox1.show()
        vbox2 = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, homogeneous=False, spacing=10)
        vbox2.set_border_width(10)
        vbox1.pack_start(vbox2, True, True, 0)
        vbox2.show()
        label = Gtk.Label(label=_("Packages mirrors are syncing with new "
                          "packages"))
        vbox2.pack_start(label, False, False, 0)
        hbox2 = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, homogeneous=False, spacing=10)
        hbox2.set_border_width(5)
        vbox1.pack_start(hbox2, False, True, 0)
        hbox2.show()
        ok_button = Gtk.Button(label=_("Close"))
        ok_button.connect("clicked", on_close, window)
        hbox2.pack_end(ok_button, False, False, 0)
        window.show_all()


class ServerUnreachable(object):
    """
    Class for the server unreachable warning window.
    """

    def __init__(self):
        """
        The constructor of the ServerUnreachable class.
        """
        window = Gtk.Window()
        window.set_position(Gtk.WindowPosition.CENTER)
        window.set_border_width(8)
        window.connect("destroy", on_close, window)
        window.set_title(_("Server Unreachable"))
        vbox1 = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, homogeneous=False, spacing=0)
        window.add(vbox1)
        vbox1.show()
        hbox2 = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, homogeneous=False, spacing=10)
        hbox2.set_border_width(10)
        vbox1.pack_start(hbox2, True, True, 0)
        hbox2.show()
        label = Gtk.Label(label=_("The server is unreachable. Your internet "
                          "could\nbe down or software package server is down."))
        hbox2.pack_start(label, False, False, 0)
        hbox2 = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, homogeneous=False, spacing=10)
        hbox2.set_border_width(5)
        vbox1.pack_start(hbox2, False, True, 0)
        hbox2.show()
        ok_button = Gtk.Button(label=_("Close"))
        ok_button.connect("clicked", on_close, window)
        hbox2.pack_end(ok_button, False, False, 0)
        window.show_all()


class SomethingIsWrong(object):
    """
    Class for the something is wrong warning window.
    """

    def __init__(self):
        """
        The constructor of the SomethingIsWrong class.
        """
        window = Gtk.Window()
        window.set_position(Gtk.WindowPosition.CENTER)
        window.set_border_width(8)
        window.connect("destroy", Gtk.main_quit)
        window.set_title(_("Something Is Wrong"))
        vbox1 = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, homogeneous=False, spacing=0)
        window.add(vbox1)
        vbox1.show()
        hbox2 = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, homogeneous=False, spacing=10)
        hbox2.set_border_width(10)
        vbox1.pack_start(hbox2, True, True, 0)
        hbox2.show()
        label = Gtk.Label(label=_(
                          "If you see this message it means that "
                          "something is wrong.\n Please look at pkg upgrade "
                          "output."))
        hbox2.pack_start(label, False, False, 0)
        hbox2 = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, homogeneous=False, spacing=10)
        hbox2.set_border_width(5)
        vbox1.pack_start(hbox2, False, True, 0)
        hbox2.show()
        ok_button = Gtk.Button(label=_("Close"))
        ok_button.connect("clicked", Gtk.main_quit)
        hbox2.pack_end(ok_button, False, False, 0)
        window.show_all()


class NotRoot:
    """
    Class for the user is not root warning window.
    """

    def __init__(self):
        """
        The constructor of the NotRoot class.
        """
        window = Gtk.Window()
        window.set_title(_("Software Station"))
        window.connect("destroy", on_close, window)
        window.set_size_request(300, 80)
        v_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, homogeneous=False, spacing=0)
        window.add(v_box)
        v_box.show()
        label = Gtk.Label(label=_('You need to be root'))
        v_box.pack_start(label, True, True, 0)
        h_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, homogeneous=False, spacing=0)
        h_box.show()
        v_box.pack_end(h_box, False, False, 5)
        ok_button = Gtk.Button()
        ok_button.set_label(_("Close"))
        ok_button.connect("clicked", on_close, window)
        h_box.pack_end(ok_button, False, False, 5)
        window.show_all()
