#!/usr/local/bin/python

import gtk
import gobject
#from subprocess import call


class TrayIcon(object):
    def __init__(self):
        self.statusIcon = gtk.StatusIcon()
        self.statusIcon.set_tooltip('System Update availeble')
        self.statusIcon.set_visible(True)

        self.menu = gtk.Menu()

        self.menu.show_all()
        self.act = False
        self.statusIcon.connect("activate", self.leftclick)
        self.statusIcon.connect('popup-menu', self.icon_clicked)

    #def nm_menu(self):
        #self.ssid_name = ssidliste()
        #self.menu = gtk.Menu()
        #e_title = gtk.MenuItem()
        #e_title.set_label("Ethernet Network")
        #e_title.set_sensitive(False)
        #self.menu.append(e_title)
        #disconnected = gtk.MenuItem()
        #if wiredonlineinfo() is True:
            #wired_item = gtk.MenuItem("Wired Connection")
            #self.menu.append(wired_item)
            #disconnect_item = gtk.ImageMenuItem("Disconnect")
            #disconnect_item.connect("activate", self.wireddisconnect)
            #self.menu.append(disconnect_item)
        #elif wiredconnectedinfo() is True:
            #disconnected.set_label("disconnected")
            #disconnected.set_sensitive(False)
            #self.menu.append(disconnected)
            #wired_item = gtk.MenuItem("Wired Connection")
            #wired_item.connect("activate", self.wiredconnect)
            #self.menu.append(wired_item)
        #else:
            #disconnected.set_label("disconnected")
            #disconnected.set_sensitive(False)
            #self.menu.append(disconnected)
        #self.menu.append(gtk.SeparatorMenuItem())
        #w_title = gtk.MenuItem()
        #w_title.set_label("Wi-Fi Network")
        #w_title.set_sensitive(False)
        #self.menu.append(w_title)
        #if get_ssid() is None:
            #pass
        #else:
            #bar = barpercent(get_ssid())
            #connection_item = gtk.ImageMenuItem(get_ssid())
            #connection_item.set_image(self.openwifi(bar))
            #connection_item.show()
            #disconnect_item = gtk.MenuItem("Disconnect")
            #disconnect_item.connect("activate", self.disconnectfromwifi)
            #self.menu.append(connection_item)
            #self.menu.append(disconnect_item)
            #self.menu.append(gtk.SeparatorMenuItem())
        #for name in self.ssid_name:
            #bar = barpercent(name)
            #if get_ssid() == name:
                #pass
            #else:
                #menu_item = gtk.ImageMenuItem(name)
                #menu_item.set_image(self.openwifi(bar))
                #if keyinfo(name) == 'EP':
                    #menu_item.connect("activate", self.menu_click_look, name)
                #elif keyinfo(name) == 'E':
                    #menu_item.connect("activate", self.menu_click_open, name)
                #menu_item.show()
                #self.menu.append(menu_item)
        #self.menu.show_all()
        #return self.menu

    def leftclick(self, status_icon):
        button = 1
        position = gtk.status_icon_position_menu
        time = gtk.get_current_event_time()
        #self.nm_menu()
        self.menu.popup(None, None, position, button, time, status_icon)

    def icon_clicked(self, status_icon, button, time):
        position = gtk.status_icon_position_menu
        self.nm_menu()
        self.menu.popup(None, None, position, button, time, status_icon)

    def openwifi(self, bar):
        img = gtk.Image()
        if bar > 75:
            img.set_from_file(sgnal100)
        elif bar > 50:
            img.set_from_file(sgnal75)
        elif bar > 25:
            img.set_from_file(sgnal50)
        elif bar > 5:
            img.set_from_file(sgnal25)
        else:
            img.set_from_file(sgnal0)
        img.show()
        return img

    def check(self):
        self.statusIcon.set_from_stock(gtk.STOCK_DIALOG_WARNING)
        return True

    def tray(self):
        self.check()
        gobject.timeout_add(10000, self.check)
        gtk.main()


i = TrayIcon()
i.tray()