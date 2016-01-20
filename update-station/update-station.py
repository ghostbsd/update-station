#!/usr/local/bin/python

import gtk as Gtk
import gobject as GObject
import threading
import sys
import locale
sys.path.append("/usr/local/lib/update-station/")
from updateHandler import lookFbsdUpdate, checkVersionUpdate, checkPkgUpdate
from updateHandler import installFreeBSDUpdate, fetchFreeBSDUpdate, pkgUpdateList
from updateHandler import fetchPkgUpdate, installPkgUpdate, checkForUpdate
from updateHandler import checkFreeBSDUpdate, cleanDesktop, CheckPkgUpdateFromFile
# ifPortsIstall
updateToInstall = []
PkgList = []
from time import sleep
from subprocess import Popen
insingal = True
encoding = locale.getpreferredencoding()
utf8conv = lambda x: str(x, encoding).encode('utf8')
threadBreak = False
GObject.threads_init()
uwinstatue = True

class UpdateWindow:

    def hidewindow(self, widget):
        self.window.hide()

    def delete_event(self, widget):
        # don't delete; hide instead
        self.window.hide_on_delete()

    def startupdate(self, widget):
        if len(updateToInstall) != 0:
            if self.insingal is True:
                installUpdate(updateToInstall, self.window)
                self.insingal = False

    def create_bbox(self, horizontal, spacing, layout):
        table = Gtk.Table(1, 5, True)
        button = Gtk.Button("Install update")
        table.attach(button, 0, 1, 0, 1)
        button.connect("clicked", self.startupdate, )
        button = Gtk.Button(stock=Gtk.STOCK_CLOSE)
        table.attach(button, 4, 5, 0, 1)
        button.connect("clicked", self.hidewindow)
        return table

    def __init__(self):
        self.insingal = True
        # window
        self.window = Gtk.Window()
        self.window.connect("destroy", self.delete_event)
        self.window.set_size_request(600, 400)
        self.window.set_resizable(False)
        self.window.set_title("Update Manager")
        self.window.set_border_width(0)
        self.window.set_position(Gtk.WIN_POS_CENTER)
        box1 = Gtk.VBox(False, 0)
        self.window.add(box1)
        box1.show()
        box2 = Gtk.VBox(False, 0)
        box2.set_border_width(20)
        box1.pack_start(box2, True, True, 0)
        box2.show()
        # Title
        titleext = "Updates available!"
        titlelabel = Gtk.Label(
            "<b><span size='large'>%s</span></b>" % titleext)
        titlelabel.set_use_markup(True)
        box2.pack_start(titlelabel, False, False, 0)
        self.tree_store = Gtk.TreeStore(GObject.TYPE_STRING,
                                        GObject.TYPE_BOOLEAN)
        sw = Gtk.ScrolledWindow()
        sw.set_shadow_type(Gtk.SHADOW_ETCHED_IN)
        sw.set_policy(Gtk.POLICY_AUTOMATIC, Gtk.POLICY_AUTOMATIC)
        sw.add(self.Display(self.store()))
        sw.show()
        box2.pack_start(sw, True, True, 10)
        box2 = Gtk.HBox(False, 10)
        box2.set_border_width(5)
        box1.pack_start(box2, False, False, 0)
        box2.show()
        # Add button
        box2.pack_start(self.create_bbox(True, 10, Gtk.BUTTONBOX_END),
                        True, True, 5)
        self.window.show_all()

    def store(self):
        self.tree_store.clear()
        if checkVersionUpdate() is True:
            self.tree_store.append(None, (lookFbsdUpdate(), True))
            if "FreeBSD Update" not in updateToInstall:
                updateToInstall.extend(["FreeBSD Update"])
        if CheckPkgUpdateFromFile() is True:
            pinter = self.tree_store.append(None, ("Software Update Available", True))
            for line in pkgUpdateList():
                self.tree_store.append(pinter, (line, True))
            if "Software Update" not in updateToInstall:
                updateToInstall.extend(["Software Update Available"])
        return self.tree_store

    def Display(self, model):
        self.view = Gtk.TreeView(model)
        self.renderer = Gtk.CellRendererText()
        self.renderer1 = Gtk.CellRendererToggle()
        self.renderer1.set_property('activatable', True)
        self.renderer1.connect('toggled', self.col1_toggled_cb, model)
        self.column0 = Gtk.TreeViewColumn("Name", self.renderer, text=0)
        self.column1 = Gtk.TreeViewColumn("Complete", self.renderer1)
        self.column1.add_attribute(self.renderer1, "active", 1)
        self.view.append_column(self.column1)
        self.view.append_column(self.column0)
        self.view.set_headers_visible(False)
        return self.view

    def col1_toggled_cb(self, cell, path, model):
        model[path][1] = not model[path][1]
        if model[path][1] is False:
            updateToInstall.remove(model[path][0].partition(':')[0])
        else:
            updateToInstall.extend([model[path][0].partition(':')[0]])
        return


class TrayIcon:
    def close_application(self, widget):
        quit()

    def __init__(self):
        # Statue Tray Code
        self.statusIcon = Gtk.StatusIcon()
        self.statusIcon.set_tooltip('Update Manager')
        self.statusIcon.set_visible(True)
        self.menu = Gtk.Menu()
        self.menu.show_all()
        self.statusIcon.connect("activate", self.leftclick)
        self.statusIcon.connect('popup-menu', self.icon_clicked)

    def nm_menu(self):
        # right click menue
        self.menu = Gtk.Menu()
        close_item = Gtk.MenuItem("Close")
        close_item.connect("activate", self.close_application)
        self.menu.append(close_item)
        self.menu.show_all()
        return self.menu

    def leftclick(self, status_icon):
        if checkForUpdate(2) is True:
            UpdateWindow()
            self.destroy()

    def icon_clicked(self, status_icon, button, time):
        position = Gtk.status_icon_position_menu
        self.nm_menu()
        self.menu.popup(None, None, position, button, time, status_icon)

    def destroy(self):
        self.statusIcon.set_visible(False)

    def updatetray(self):
        if checkForUpdate(1) is True:
            self.statusIcon.set_visible(True)
            self.statusIcon.set_from_stock(Gtk.STOCK_DIALOG_INFO)
        else:
            self.statusIcon.set_visible(False)

    def TreadingUpdate(self):
        thr = threading.Thread(target=self.check)
        thr.setDaemon(True)
        thr.start()

    def check(self):
        while True:
            checkFreeBSDUpdate()
            self.updatetray()
            sleep(1200)
        return True



def read_output(window, probar, installupdate, window1):
    howMany = len(installupdate)
    fraction = 1.0 / int(howMany)
    if "FreeBSD Update" in installupdate:
        probar.set_text("Fetching FreeBSD updates")
        sleep(1)
        dfu = fetchFreeBSDUpdate()
        while 1:
            line = dfu.readline()
            if not line:
                break
            bartest = line
            probar.set_text("%s" % bartest.rstrip())
        probar.set_text("FreeBSD updates downloaded")
        probar.set_fraction(fraction)
        sleep(1)
        probar.set_text("Installing FreeBSD updates")
        ifu = installFreeBSDUpdate()
        while 1:
            line = ifu.readline()
            if not line:
                break
            bartest = line
            probar.set_text("%s" % bartest.rstrip())
        probar.set_text("FreeBSD updates installed")
        probar.set_fraction(fraction)
        sleep(1)
    if "Software Update Available" in installupdate:
        probar.set_text("Fetching packages updates")
        sleep(1)
        fpu = fetchPkgUpdate()
        while 1:
            line = fpu.readline()
            if not line:
                break
            bartest = line
            probar.set_text("%s" % bartest.rstrip())
        probar.set_text("Packages updates downloaded")
        sleep(1)
        probar.set_text("Installing packages updates")
        sleep(1)
        ipu = installPkgUpdate()
        while 1:
            line = ipu.readline()
            if not line:
                break
            bartest = line
            probar.set_text("%s" % bartest.rstrip())
        probar.set_text("Packages updates installed")
        probar.set_fraction(fraction)
        sleep(1)
        probar.set_text("Cleaning Desktop Icon")
        cleanDesktop()
        probar.set_text("Cleaning Done")
        sleep(1)
        # need to add a script to set pkg after pkg update.
    window.hide()
    window1.hide()
    if "FreeBSD Update" in installupdate:
        restartSystem()
    else:
        Successful()


class installUpdate:
    def close_application(self, widget):
        Gtk.main_quit()

    def __init__(self, installupdate, window):
        self.win = Gtk.Window()
        self.win.connect("delete-event", Gtk.main_quit)
        self.win.set_size_request(500, 75)
        self.win.set_resizable(False)
        self.win.set_title("installing Update")
        self.win.set_border_width(0)
        self.win.set_position(Gtk.WIN_POS_CENTER)
        box1 = Gtk.VBox(False, 0)
        self.win.add(box1)
        box1.show()
        box2 = Gtk.VBox(False, 10)
        box2.set_border_width(10)
        box1.pack_start(box2, True, True, 0)
        box2.show()
        self.pbar = Gtk.ProgressBar()
        self.pbar.set_orientation(Gtk.PROGRESS_LEFT_TO_RIGHT)
        self.pbar.set_fraction(0.0)
        self.pbar.set_size_request(-1, 20)
        box2.pack_start(self.pbar, False, False, 0)
        self.win.show_all()
        thr = threading.Thread(target=read_output,
                               args=(self.win, self.pbar, installupdate,
                                     window))
        thr.setDaemon(True)
        thr.start()


class initialInstall:
    def __init__(self):
        self.win = Gtk.Window()
        self.win.connect("delete-event", Gtk.main_quit)
        # self.win.set_size_request(500, 75)
        self.win.set_resizable(False)
        self.win.set_title("Initial Installation Before Update")
        self.win.set_border_width(0)
        self.win.set_position(Gtk.WIN_POS_CENTER)
        box1 = Gtk.VBox(False, 0)
        self.win.add(box1)
        box1.show()
        box2 = Gtk.VBox(False, 10)
        box2.set_border_width(10)
        box1.pack_start(box2, True, True, 0)
        box2.show()
        self.port = Gtk.CheckButton("FreeBSD ports installation")
        self.src = Gtk.CheckButton("FreeBSD Source(Recommended for ports)")
        box2.pack_start(self.port, False, False, 0)
        box2.pack_start(self.src, False, False, 0)
        self.win.show_all()

rtxt = """In order to complete the update of your system it needs to restart."""

class restartSystem():
    def on_reboot(self, widget):
        Popen('shutdown -r now', shell=True)
        Gtk.main_quit()

    def on_close(self, widget, window):
        window.hide()

    def __init__(self):
        window = Gtk.Window()
        window.set_position(Gtk.WIN_POS_CENTER)
        window.set_border_width(8)
        window.connect("destroy", self.on_close)
        window.set_title("Update Completed")
        box1 = Gtk.VBox(False, 0)
        window.add(box1)
        box1.show()
        box2 = Gtk.VBox(False, 10)
        box2.set_border_width(10)
        box1.pack_start(box2, True, True, 0)
        box2.show()
        label = Gtk.Label(rtxt)
        box2.pack_start(label)
        box2 = Gtk.HBox(False, 10)
        box2.set_border_width(5)
        box1.pack_start(box2, False, True, 0)
        box2.show()
        table = Gtk.Table(1, 2, True)
        restart = Gtk.Button("Restart")
        restart.connect("clicked", self.on_reboot)
        Continue = Gtk.Button("Continue")
        Continue.connect("clicked", self.on_close, window)
        table.attach(Continue, 0, 1, 0, 1)
        table.attach(restart, 1, 2, 0, 1)
        box2.pack_start(table)
        window.show_all()

stxt = """Update successfully completed."""

class Successful:
    def on_close(self, widget, window):
        window.hide()

    def __init__(self):
        window = Gtk.Window()
        window.set_position(Gtk.WIN_POS_CENTER)
        window.set_border_width(8)
        window.connect("destroy", self.on_close)
        window.set_title("Update Completed")
        box1 = Gtk.VBox(False, 0)
        window.add(box1)
        box1.show()
        box2 = Gtk.VBox(False, 10)
        box2.set_border_width(10)
        box1.pack_start(box2, True, True, 0)
        box2.show()
        label = Gtk.Label(stxt)
        box2.pack_start(label)
        box2 = Gtk.HBox(False, 10)
        box2.set_border_width(5)
        box1.pack_start(box2, False, True, 0)
        box2.show()
        table = Gtk.Table(1, 2, True)
        restart = Gtk.Button("Close")
        restart.connect("clicked", self.on_close, window)
        table.attach(restart, 1, 2, 0, 1)
        box2.pack_start(table)
        window.show_all()


class UpdateManager:
    TrayIcon().TreadingUpdate()

# initialInstall()
UpdateManager()
Gtk.main()