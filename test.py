import gi
gi.require_version('Gtk', '3.0')
gi.require_version('Notify', '0.7')
from gi.repository import Gtk, Notify, GLib


class App():
    def __init__(self):
        self.last_notification = None
        Notify.init('Test')
        self.check()

    def check(self):
        self.last_notification = Notify.Notification.new('Test')
        self.last_notification.add_action('clicked', 'Action',
                                          self.notification_callback, None)
        self.last_notification.show()
        # GLib.timeout_add_seconds(10, self.check)

    def notification_callback(self, notification, action_name, data):
        print(action_name)
        notification.close()

app = App()
# GLib.MainLoop().run()
Gtk.main()