#!/usr/local/bin/python

import gtk as Gtk
import gobject as GObject
import threading
import sys
import locale
sys.path.append("/home/ericbsd/update-station/update-station")
from updateHandler import lookFbsdUpdate, checkFbsdUpdate, checkPkgUpdate

updateToInstall = []


class updateManager:
    def close_application(self, widget):
        quit()

    def hideWindow(self, widget):
        self.window.hide()

    def delete_event(self, widget):
        #don't delete; hide instead
        self.window.hide_on_delete()
        return True

    def startupdate(self, widget):
        installUpdate(updateToInstall)

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
        self.window = Gtk.Window()
        self.window.connect("delete-event", self.delete_event)
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
        self.mdl = self.Store()
        self.view = self.Display(self.mdl)
        sw = Gtk.ScrolledWindow()
        sw.set_shadow_type(Gtk.SHADOW_ETCHED_IN)
        sw.set_policy(Gtk.POLICY_AUTOMATIC, Gtk.POLICY_AUTOMATIC)
        sw.add(self.view)
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
        self.menu = Gtk.Menu()
        close_item = Gtk.MenuItem("Close")
        close_item.connect("activate", self.close_application)
        self.menu.append(close_item)
        self.menu.show_all()
        return self.menu

    def Store(self):
        self.tree_store = Gtk.TreeStore(GObject.TYPE_STRING,
        GObject.TYPE_BOOLEAN)
        if checkFbsdUpdate() is True:
            self.tree_store.append(None, (lookFbsdUpdate(), True))
            updateToInstall.extend([lookFbsdUpdate()])
        if checkPkgUpdate() is True:
            self.tree_store.append(None, ("Software Update Available", True))
            updateToInstall.extend(["Software Update Available"])
        print updateToInstall
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
            updateToInstall.remove(model[path][0])
        else:
            updateToInstall.extend([model[path][0]])
        print updateToInstall
        return

    def leftclick(self, status_icon):
        self.window.show_all()

    def icon_clicked(self, status_icon, button, time):
        position = Gtk.status_icon_position_menu
        self.nm_menu()
        self.menu.popup(None, None, position, button, time, status_icon)

    def check(self):
        self.statusIcon.set_from_stock(Gtk.STOCK_DIALOG_WARNING)
        return True

    def tray(self):
        self.statusIcon.set_from_stock(Gtk.STOCK_DIALOG_WARNING)
        Gtk.main()


encoding = locale.getpreferredencoding()
utf8conv = lambda x: str(x, encoding).encode('utf8')
threadBreak = False
GObject.threads_init()


def read_output(command, window, probar, installUpdate):
    probar.set_text("Beginning installation")
    probar.set_fraction(0.1)
    #while True:
        #new_val = probar.get_fraction() + 0.3
        #probar.set_fraction(new_val)
        #break
    #GObject.idle_add(window.destroy)


class installUpdate:
    def close_application(self, widget):
        Gtk.main_quit()

    def __init__(self, installUpdate):
        self.win = Gtk.Window()
        self.win.connect("delete-event", Gtk.main_quit)
        self.win.set_size_request(600, 150)
        self.win.set_resizable(False)
        self.win.set_title("Update Manager")
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
        command = "install"
        thr = threading.Thread(target=read_output,
        args=(command, self.win, self.pbar, installUpdate))
        thr.start()

#installUpdate()
updateManager().tray()


def responseToDialog(entry, dialog, response):
    dialog.response(response)


def getText():
    dialog = Gtk.MessageDialog(None,
        Gtk.DIALOG_MODAL | Gtk.DIALOG_DESTROY_WITH_PARENT,
        Gtk.MESSAGE_QUESTION, Gtk.BUTTONS_OK, None)
    dialog.set_markup('Please enter your passord:')
    entry = Gtk.Entry()
    entry.set_visibility(False)
    entry.connect("activate", responseToDialog, dialog, Gtk.RESPONSE_OK)
    hbox = Gtk.HBox()
    hbox.pack_start(Gtk.Label("Password:"), False, 5, 5)
    hbox.pack_end(entry)
    dialog.format_secondary_markup(
    "This will be used for <i>identification</i> purposes")
    dialog.vbox.pack_end(hbox, True, True, 0)
    dialog.show_all()
    dialog.run()
    text = entry.get_text()
    dialog.destroy()
    return text

updateManager().tray()