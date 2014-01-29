#!/usr/local/bin/python

import gtk


class Entire():

    def close_application(self, widget):
        gtk.main_quit()

    def __init__(self):
        window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        window.connect("destroy", self.close_application)
        window.set_size_request(700, 500)
        window.set_resizable(False)
        window.set_title("Update Manager")
        window.set_border_width(0)
        window.set_position(gtk.WIN_POS_CENTER)
        window.set_icon_from_file("/usr/local/etc/gbi/logo.png")
        box1 = gtk.VBox(False, 0)
        window.add(box1)
        box1.show()
        box2 = gtk.VBox(False, 10)
        box2.set_border_width(20)
        box1.pack_start(box2, True, True, 0)
        box2.show()
        # Title
        titleText = "System updates available!"
        Title = gtk.Label("<b><span size='large'>%s</span></b>" % titleText)
        Title.set_use_markup(True)
        box2.pack_start(Title, False, False, 0)
        # chose Disk

        sw = gtk.ScrolledWindow()
        sw.set_shadow_type(gtk.SHADOW_ETCHED_IN)
        sw.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        store = gtk.TreeStore(str, 'gboolean')
        #for disk in disk_query():
        store.append(None, ["FreeBSD 10.0-p1 update", True])
        treeView = gtk.TreeView(store)
        treeView.set_model(store)
        treeView.set_rules_hint(True)
        cell = gtk.CellRendererText()
        column = gtk.TreeViewColumn(None, cell, text=0)
        column_header = gtk.Label('Update')
        column_header.set_use_markup(True)
        column_header.show()
        column.set_widget(column_header)
        column.set_sort_column_id(0)
        #cell2 = gtk.CellRendererText()
        #column2 = gtk.TreeViewColumn(None, cell2, text=0)
        #column_header2 = gtk.Label('Size(MB)')
        #column_header2.set_use_markup(True)
        #column_header2.show()
        #column2.set_widget(column_header2)
        #cell3 = gtk.CellRendererText()
        #column3 = gtk.TreeViewColumn(None, cell3, text=0)
        #column_header3 = gtk.Label('Scheme')
        #column_header3.set_use_markup(True)
        #column_header3.show()
        #column3.set_widget(column_header3)
        column.set_attributes(cell, text=0)
        #column2.set_attributes(cell2, text=1)
        #column3.set_attributes(cell3, text=2)
        treeView.append_column(column)
        treeView.set_headers_visible(False)
        #treeView.append_column(column2)
        #treeView.append_column(column3)
        tree_selection = treeView.get_selection()
        tree_selection.set_mode(gtk.SELECTION_SINGLE)
        #tree_selection.connect("changed", self.Selection_Variant)
        sw.add(treeView)
        sw.show()
        box2.pack_start(sw, True, True, 10)
        box2 = gtk.HBox(False, 10)
        box2.set_border_width(5)
        box1.pack_start(box2, False, False, 0)
        box2.show()
        # Add button
        #box2.pack_start(use_disk_bbox(True,
                        #10, gtk.BUTTONBOX_END),
                        #True, True, 5)
        window.show_all()

Entire()
gtk.main()