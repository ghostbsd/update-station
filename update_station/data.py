import getpass
import os


class Data:
    """
    Class that contains all the data that is used by the update-station.

    Attributes:
        backup: Boolean that indicates if the update-station should back up the current boot environment.
        be_name: String that contains the name of the backup or upgrade boot environment.
        be_mount_path: String that contains the mount path of the upgrade boot environment.
        close_session: Boolean that indicates if the update-station should close the session.
        current_abi: String that indicates the current ABI of the system.
        current_version: String that indicates the current version of the system.
        do_not_upgrade: Boolean that indicates if the update-station should not upgrade the system.
        home: String that indicates the home directory of the user that is running the update-station.
        packages_dictionary: Dictionary that contains all the packages that are installed on the system.
        new_abi: String that indicates the new ABI of the system.
        new_version: String that indicates the new version of the system.
        second_update: Boolean that indicates if the update-station should do 2 update.
        stop_pkg_refreshing: Boolean that indicates if the update-station should stop refreshing the packages.
        system_tray: Object that contains the system tray of the update-station.
        update_started: Boolean that indicates if the application has started updating the system.
        upgrade_type: String that indicates the kind of upgrade installed in a new boot environment:
            'major' (FreeBSD ABI change), 'minor' (FreeBSD minor release change),
            'release' (GhostBSD release change only) or 'none' for in-place package updates.
        username: String that indicates the username of the user that is running the update-station.
    """
    backup: bool = False
    be_name: str = ''
    be_mount_path: str = ''
    close_session: bool = False
    current_abi: str = ''
    current_version: str = ''
    do_not_upgrade: bool = False
    home: str = os.path.expanduser('~')
    new_abi: str = ''
    new_version: str = ''
    packages_dictionary: dict = {}
    second_update: bool = False
    stop_pkg_refreshing: bool = False
    system_tray = None
    update_started: bool = False
    upgrade_type: str = 'none'
    username: str = os.environ.get('SUDO_USER') if 'SUDO_USER' in os.environ else getpass.getuser()

    @classmethod
    def be_upgrade(cls) -> bool:
        """
        Check if the upgrade is installed in a new boot environment.

        :return: True for major, minor and release upgrades, False for in-place package updates.
        """
        return cls.upgrade_type != 'none'

    @classmethod
    def force_reinstall(cls) -> bool:
        """
        Check if every package must be reinstalled because the FreeBSD version changes.

        :return: True for major and minor upgrades, False otherwise.
        """
        return cls.upgrade_type in ('major', 'minor')

    @classmethod
    def upgrade_abi(cls) -> str | None:
        """
        Get the ABI pkg must use for the upgrade.

        A major upgrade is the only one served by another ABI repository.

        :return: The new ABI for a major upgrade, None to keep the ABI of the running system otherwise.
        """
        return cls.new_abi if cls.upgrade_type == 'major' else None
