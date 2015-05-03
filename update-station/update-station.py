#!/usr/local/bin/python

import gtk as Gtk
import gobject as GObject
import threading
import sys
import locale
sys.path.append("/usr/local/lib/update-station/")
from updateHandler import lookFbsdUpdate, checkVersionUpdate, checkPkgUpdate
from updateHandler import installFreeBSDUpdate, fetchFreeBSDUpdate
from updateHandler import fetchPkgUpdate, installPkgUpdate, checkForUpdate
from updateHandler import checkFreeBSDUpdate, ifPortsIstall
updateToInstall = []
from time import sleep
insingal = True
encoding = locale.getpreferredencoding()
utf8conv = lambda x: str(x, encoding).encode('utf8')
threadBreak = False
GObject.threads_init()


class updateManager:
    def close_application(self, widget):
        quit()

    def hideWindow(self, widget):
        self.window.hide()
        self.insingal = True

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
        button.connect("clicked", self.startupdate)
        button = Gtk.Button(stock=Gtk.STOCK_CLOSE)
        table.attach(button, 4, 5, 0, 1)
        button.connect("clicked", self.hideWindow)
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
        titleText = "Updates available!"
        Title = Gtk.Label("<b><span size='large'>%s</span></b>" % titleText)
        Title.set_use_markup(True)
        box2.pack_start(Title, False, False, 0)
        self.tree_store = Gtk.TreeStore(GObject.TYPE_STRING,
                                        GObject.TYPE_BOOLEAN)
        sw = Gtk.ScrolledWindow()
        sw.set_shadow_type(Gtk.SHADOW_ETCHED_IN)
        sw.set_policy(Gtk.POLICY_AUTOMATIC, Gtk.POLICY_AUTOMATIC)
        sw.add(self.Display(self.Store()))
        sw.show()
        box2.pack_start(sw, True, True, 10)
        box2 = Gtk.HBox(False, 10)
        box2.set_border_width(5)
        box1.pack_start(box2, False, False, 0)
        box2.show()
        # Add button
        box2.pack_start(self.create_bbox(True,
                                         10, Gtk.BUTTONBOX_END), True, True, 5)
        # Statue Tray Code
        self.statusIcon = Gtk.StatusIcon()
        self.statusIcon.set_tooltip('System Update availeble')
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

    def Store(self):
        self.tree_store.clear()
        if checkVersionUpdate() is True:
            self.tree_store.append(None, (lookFbsdUpdate(), True))
            updateToInstall.extend([lookFbsdUpdate().partition(':')[0]])
        if checkPkgUpdate() is True:
            self.tree_store.append(None, ("Software Update Available", True))
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

    def leftclick(self, status_icon):
        if checkForUpdate(2) is True:
            self.Store()
            self.window.show_all()

    def icon_clicked(self, status_icon, button, time):
        position = Gtk.status_icon_position_menu
        self.nm_menu()
        self.menu.popup(None, None, position, button, time, status_icon)

    def check(self):
        while True:
            if checkForUpdate(1) is True:
                self.statusIcon.set_from_stock(Gtk.STOCK_NO)
            else:
                self.statusIcon.set_from_stock(Gtk.STOCK_YES)
            sleep(60)
        return True

    def tray(self):
        self.statusIcon.set_from_stock(Gtk.STOCK_NO)
        thr = threading.Thread(target=self.check)
        thr.setDaemon(True)
        thr.start()
        Gtk.main()


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
            print bartest
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
        # need to add a script to set pkg after pkg update.
    GObject.idle_add(window.destroy)
    GObject.idle_add(window1.destroy)
    print "DONE"


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
                               args=(self.win, self.pbar, installupdate, window))
        thr.setDaemon(True)
        thr.start()


class initialInstall:
    def __init__(self):
        self.win = Gtk.Window()
        self.win.connect("delete-event", Gtk.main_quit)
        #self.win.set_size_request(500, 75)
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

#if ifPortsIstall() is False:
#    initialInstall()

checkFreeBSDUpdate()
updateManager().tray()
