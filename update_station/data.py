import getpass
import os


class Data:
    """
    Class that contains all the data that is used by the update-station.

    Attributes:
        backup: Boolean that indicates if the update-station should back up the current boot environment.
        close_session: Boolean that indicates if the update-station should close the session.
        current_abi: String that indicates the current ABI of the system.
        do_not_upgrade: Boolean that indicates if the update-station should not upgrade the system.
        home: String that indicates the home directory of the user that is running the update-station.
        system_upgrade: Boolean that indicates if the update-station should upgrade the kernel.
        packages_dictionary: Dictionary that contains all the packages that are installed on the system.
        major_upgrade: Boolean that indicates if the update-station should do a major upgrade.
        new_abi: String that indicates the new ABI of the system.
        second_update: Boolean that indicates if the update-station should do 2 update.
        stop_pkg_refreshing: Boolean that indicates if the update-station should stop refreshing the packages.
        system_tray: Object that contains the system tray of the update-station.
        update_started: Boolean that indicates if the application has started updating the system.
        username: String that indicates the username of the user that is running the update-station.
    """
    backup: bool = False
    close_session: bool = False
    current_abi: str = ''
    do_not_upgrade: bool = False
    home: str = os.path.expanduser('~')
    system_upgrade: bool = False
    major_upgrade: bool = False
    new_abi: str = ''
    packages_dictionary: dict = {}
    second_update: bool = False
    stop_pkg_refreshing: bool = False
    system_tray = None
    update_started: bool = False
    username: str = os.environ.get('SUDO_USER') if 'SUDO_USER' in os.environ else getpass.getuser()
