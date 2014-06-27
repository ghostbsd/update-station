#!/usr/local/bin/python

import gtk
import gobject
import sys
sys.path.append("/usr/home/ericbsd/update-station/updatemgr")
from updateHandler import lookUpdate, updateText

class GUI_Controller:
    def close_application(self, widget):
        gtk.main_quit()

    def hideWindow(self, widget):
        self.window.hide()

    def create_bbox(self, horizontal, spacing, layout):
        bbox = gtk.HButtonBox()
        bbox.set_border_width(10)
        bbox.set_spacing(10)
        button = gtk.Button(stock=gtk.STOCK_PREFERENCES)
        #button.connect("clicked", root_window)
        bbox.add(button)
        button = gtk.Button(stock=gtk.STOCK_CLOSE)
        bbox.add(button)
        button.connect("clicked", self.hideWindow)
        return bbox

    def install_bbox(self, horizontal, spacing, layout):
        bbox = gtk.HButtonBox()
        bbox.set_border_width(10)
        bbox.set_layout(layout)
        bbox.set_spacing(10)
        #button = gtk.Button(stock=gtk.STOCK_PREFERENCES)
        #button.connect("clicked", root_window)
        #bbox.add(button)
        button = gtk.Button('Install update')
        bbox.add(button)
        button.connect("clicked", self.close_application)
        return bbox

    def __init__(self):
        self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.window.connect("destroy", self.close_application)
        self.window.set_size_request(700, 550)
        self.window.set_resizable(False)
        self.window.set_title("Update Manager")
        self.window.set_border_width(0)
        self.window.set_position(gtk.WIN_POS_CENTER)
        #window.set_icon_from_file("/usr/local/etc/gbi/logo.png")
        box1 = gtk.VBox(False, 0)
        self.window.add(box1)
        box1.show()
        #box1.set_border_width(20)
        box2 = gtk.VBox(False, 0)
        box2.set_border_width(20)
        box1.pack_start(box2, True, True, 0)
        box2.show()
        # Title
        titleText = "System updates available!"
        Title = gtk.Label("<b><span size='large'>%s</span></b>" % titleText)
        Title.set_use_markup(True)
        box2.pack_start(Title, False, False, 0)
        self.mdl = Store.get_model()
        self.view = Display.make_view(self.mdl)
        sw = gtk.ScrolledWindow()
        sw.set_shadow_type(gtk.SHADOW_ETCHED_IN)
        sw.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        sw.add(self.view)
        sw.show()
        box2.pack_start(sw, True, True, 10)
        box2.pack_start(self.install_bbox(True,
        10, gtk.BUTTONBOX_END), False, False, 5)
        sw = gtk.ScrolledWindow()
        sw.set_shadow_type(gtk.SHADOW_ETCHED_IN)
        sw.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        textview = gtk.TextView()
        textbuffer = textview.get_buffer()
        sw.add(textview)
        sw.show()
        textview.show()
        textview.set_editable(False)
        textview.set_cursor_visible(False)
        textbuffer.set_text(updateText())
        box2.pack_start(sw, True, True, 10)
        box2 = gtk.HBox(False, 10)
        box2.set_border_width(5)
        box1.pack_start(box2, False, False, 0)
        #box1.set_border_width(0)
        box2.show()
        # Add button
        box2.pack_start(self.create_bbox(True,
        10, gtk.BUTTONBOX_END), True, True, 5)
        self.window.show_all()


class InfoModel:

    def __init__(self):
        self.tree_store = gtk.TreeStore(gobject.TYPE_STRING,
        gobject.TYPE_BOOLEAN)

        self.tree_store.append(None, (lookUpdate(), True))
        return

    def get_model(self):
        if self.tree_store:
            return self.tree_store
        else:
            return None


class DisplayModel:

    def make_view(self, model):
        self.view = gtk.TreeView(model)
        self.renderer = gtk.CellRendererText()
        self.renderer1 = gtk.CellRendererToggle()
        self.renderer1.set_property('activatable', True)
        self.renderer1.connect('toggled', self.col1_toggled_cb, model)
        self.column0 = gtk.TreeViewColumn("Name", self.renderer, text=0)
        self.column1 = gtk.TreeViewColumn("Complete", self.renderer1)
        self.column1.add_attribute(self.renderer1, "active", 1)
        self.view.append_column(self.column1)
        self.view.append_column(self.column0)
        self.view.set_headers_visible(False)
        return self.view

    def col1_toggled_cb(self, cell, path, model):
        model[path][1] = not model[path][1]
        print(("Toggle '%s' to: %s" % (model[path][0], model[path][1],)))
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

#password = getText()
Store = InfoModel()
Display = DisplayModel()