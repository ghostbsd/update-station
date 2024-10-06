"""This module contains common functions to avoid code duplication."""

from gi.repository import Gtk
from update_station.data import Data


def update_progress(progress, fraction, text):
    """
    Function that updates the progress bar.
    :param progress: The progress bar.
    :param fraction: The fraction to add.
    :param text: The text to display.
    """
    new_val = progress.get_fraction() + fraction
    progress.set_fraction(new_val)
    progress.set_text(text)


def on_close(*args):
    """
    This function to close the window or quit the application if Data.close_session is True.
    :param args: Additional arguments. The last argument must be the Gtk.Window object.
    """
    window = args[-1]
    # Ensure the last argument is a Gtk.Window
    assert isinstance(window, Gtk.Window), "The last argument must be a Gtk.Window"
    if Data.close_session is True:
        Gtk.main_quit()
    else:
        window.destroy()
