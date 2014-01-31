#!/usr/local/bin/python

import gtk
import gobject
from updateHandler import lookUpdate


class GUI_Controller:

    def close_application(self, widget):
        gtk.main_quit()

    def create_bbox(self, horizontal, spacing, layout):
        bbox = gtk.HButtonBox()
        bbox.set_border_width(10)
        bbox.set_spacing(10)
        button = gtk.Button(stock=gtk.STOCK_PREFERENCES)
        #button.connect("clicked", root_window)
        bbox.add(button)
        button = gtk.Button(stock=gtk.STOCK_CLOSE)
        bbox.add(button)
        button.connect("clicked", self.close_application)
        return bbox

    def __init__(self):
        window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        window.connect("destroy", self.close_application)
        window.set_size_request(700, 550)
        window.set_resizable(False)
        window.set_title("Update Manager")
        window.set_border_width(0)
        window.set_position(gtk.WIN_POS_CENTER)
        window.set_icon_from_file("/usr/local/etc/gbi/logo.png")
        box1 = gtk.VBox(False, 0)
        window.add(box1)
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
        box2.pack_start(self.create_bbox(True,
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
        infile = open("mainWindow.py", "r")
        if infile:
            string = infile.read()
            infile.close()
            textbuffer.set_text(string)
        box2.pack_start(sw, True, True, 10)
        box2 = gtk.HBox(False, 10)
        box2.set_border_width(5)
        box1.pack_start(box2, False, False, 0)
        #box1.set_border_width(0)
        box2.show()
        # Add button
        box2.pack_start(self.create_bbox(True,
        10, gtk.BUTTONBOX_END), True, True, 5)
        window.show_all()


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

Store = InfoModel()
Display = DisplayModel()
GUI_Controller()
gtk.main()