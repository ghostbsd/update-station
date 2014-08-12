#!/usr/local/bin/python

import gtk as Gtk
import gobject as GObject
import sys
#from gi.repository import Gtk
#from gi.repository import GObject
sys.path.append("/home/ericbsd/update-station/updatemgr")
from updateHandler import lookFbsdUpdate, updateText, checkFbsdUpdate

class Window:
    def close_application(self, widget):
        gtk.main_quit()

    def hideWindow(self, widget):
        self.window.hide()

    def create_bbox(self, horizontal, spacing, layout):
        table = Gtk.Table(1, 5, True)
        #button = Gtk.Button(stock=Gtk.STOCK_PREFERENCES)
        #button.connect("clicked", root_window)
        #bbox.add(button)table = Gtk.Table(1, 5, True)
        button = Gtk.Button("Install update")
        table.attach(button, 0, 1, 0, 1)
        button.connect("clicked", self.close_application)
        button = Gtk.Button(stock=Gtk.STOCK_CLOSE)
        table.attach(button, 4, 5, 0, 1)
        button.connect("clicked", self.hideWindow)
        return table

    def install_bbox(self, horizontal, spacing, layout):
        table = Gtk.Table(1, 5, True)
        button = Gtk.Button("Install update")
        table.attach(button, 4, 5, 0, 1)
        button.connect("clicked", self.close_application)
        return table

    def __init__(self):
        #Gtk.WINDOW_TOPLEVEL
        self.window = Gtk.Window()
        self.window.connect("destroy", self.close_application)
        self.window.set_size_request(600, 400)
        self.window.set_resizable(False)
        self.window.set_title("Update Manager")
        self.window.set_border_width(0)
        #self.window.set_position(Gtk.WIN_POS_CENTER)
        #window.set_icon_from_file("/usr/local/etc/gbi/logo.png")
        box1 = Gtk.VBox(False, 0)
        self.window.add(box1)
        box1.show()
        #box1.set_border_width(20)
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
        #box2.pack_start(self.install_bbox(True,
        #10, Gtk.BUTTONBOX_END), False, False, 0)
        #sw = Gtk.ScrolledWindow()
        #sw.set_shadow_type(Gtk.SHADOW_ETCHED_IN)
        #sw.set_policy(Gtk.POLICY_AUTOMATIC, Gtk.POLICY_AUTOMATIC)
        #textview = Gtk.TextView()
        #textbuffer = textview.get_buffer()
        #sw.add(textview)
        #sw.show()
        #textview.show()
        #textview.set_editable(False)
        #textview.set_cursor_visible(False)
        #textbuffer.set_text(updateText())
        #box2.pack_start(sw, True, True, 10)
        box2 = Gtk.HBox(False, 10)
        box2.set_border_width(5)
        box1.pack_start(box2, False, False, 0)
        #box1.set_border_width(0)
        box2.show()
        # Add button
        box2.pack_start(self.create_bbox(True,
        10, Gtk.BUTTONBOX_END), True, True, 5)
        self.window.show_all()

    def Store(self):
        self.tree_store = Gtk.TreeStore(GObject.TYPE_STRING,
        GObject.TYPE_BOOLEAN)
        print checkFbsdUpdate()
        if checkFbsdUpdate() is True:
            self.tree_store.append(None, (lookFbsdUpdate(), True))
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
        print(("Toggle '%s' to: %s" % (model[path][0], model[path][1],)))
        self.fbsysupdate = model[path][1]
        return


def responseToDialog(entry, dialog, response):
    dialog.response(response)


def getText():
    #base this on a message dialog
    dialog = gtk.MessageDialog(
        None,
        gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
        gtk.MESSAGE_QUESTION,
        gtk.BUTTONS_OK,
        None)
    dialog.set_markup('Please enter your passord:')
    #create the text input field
    entry = gtk.Entry()
    entry.set_visibility(False)
    #allow the user to press enter to do ok
    entry.connect("activate", responseToDialog, dialog, gtk.RESPONSE_OK)
    #create a horizontal box to pack the entry and a label
    hbox = gtk.HBox()
    hbox.pack_start(gtk.Label("Password:"), False, 5, 5)
    hbox.pack_end(entry)
    #some secondary text
    dialog.format_secondary_markup("This will be used for <i>identification</i> purposes")
    #add it and show it
    dialog.vbox.pack_end(hbox, True, True, 0)
    dialog.show_all()
    #go go go
    dialog.run()
    text = entry.get_text()
    dialog.destroy()
    return text


Window()
Gtk.main()
