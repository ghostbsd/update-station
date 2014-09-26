#!/usr/local/bin/python

import gtk
#import gobject
from sys import path
path.append("/home/ericbsd/update-station/update-station/")
from window import Window


class TrayIcon():
    def close_application(self, widget):
        quit()

    def __init__(self):
        self.statusIcon = gtk.StatusIcon()
        self.statusIcon.set_tooltip('System Update availeble')
        self.statusIcon.set_visible(True)
        self.menu = gtk.Menu()
        self.menu.show_all()
        self.act = False
        self.statusIcon.connect("activate", self.leftclick)
        self.statusIcon.connect('popup-menu', self.icon_clicked)

    def nm_menu(self):
        self.menu = gtk.Menu()
        #disconnected = gtk.MenuItem()
        #set_item = gtk.MenuItem("Setting")
        #self.menu.append(set_item)
        #set_item.connect("activate", self.wireddisconnect)
        close_item = gtk.MenuItem("Close")
        close_item.connect("activate", self.close_application)
        self.menu.append(close_item)
        self.menu.show_all()
        return self.menu

    def leftclick(self, status_icon):
            Window()

    def icon_clicked(self, status_icon, button, time):
        position = gtk.status_icon_position_menu
        self.nm_menu()
        self.menu.popup(None, None, position, button, time, status_icon)

    def check(self):
        self.statusIcon.set_from_stock(gtk.STOCK_DIALOG_WARNING)
        return True

    def tray(self):
        self.statusIcon.set_from_stock(gtk.STOCK_DIALOG_WARNING)
        print('allo')
        #gobject.timeout_add(10000, self.check)
        gtk.main()


icon = TrayIcon()
icon.tray()