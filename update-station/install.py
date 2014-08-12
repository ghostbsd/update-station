#!/usr/local/bin/python

import gtk as Gtk
import gobject as GObject
import sys
#from gi.repository import Gtk
#from gi.repository import GObject
sys.path.append("/home/ericbsd/update-station/updatemgr")

class installUpdate:
    def close_application(self, widget):
        gtk.main_quit()

    def __init__(self):
        self.win = Gtk.Window()
        self.win.connect("delete-event", Gtk.main_quit)
        self.win.set_size_request(600, 150)
        self.win.set_resizable(False)
        self.win.set_title("Update Manager")
        self.win.set_border_width(0)
        self.win.set_position(Gtk.WindowPosition.CENTER)
        box1 = Gtk.VBox(False, 0)
        self.win.add(box1)
        box1.show()
        box2 = Gtk.VBox(False, 10)
        box2.set_border_width(10)
        box1.pack_start(box2, True, True, 0)
        box2.show()
        self.pbar = Gtk.ProgressBar()
        #self.pbar.set_orientation(Gtk.PROGRESS_LEFT_TO_RIGHT)
        self.pbar.set_fraction(0.0)
        self.pbar.set_size_request(-1, 20)
        #self.timer = gobject.timeout_add(150, progress_timeout, self.pbar)
        box2.pack_start(self.pbar, False, False, 0)
        self.win.show_all()
        #command = '%s -c %spcinstall.cfg' % (sysinstall, tmp)
        #thr = threading.Thread(target=read_output,
        #args=(command, window, self.pbar))
        #thr.start()
        
installUpdate()
