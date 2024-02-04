class Data:
    """
    Cla
    Attributes:
        backup: Boolean that indicates if the update-station should back up the current boot environment.
        close_session: Boolean that indicates if the update-station should close the session.
        current_abi: String that indicates the current ABI of the system.
        do_not_upgrade: Boolean that indicates if the update-station should not upgrade the system.
        packages_dictionary: Dictionary that contains all the packages that are installed on the system.
        major_upgrade: Boolean that indicates if the update-station should do a major upgrade.
        new_abi: String that indicates the new ABI of the system.
        second_update: Boolean that indicates if the update-station should do 2 update.
        stop_pkg_refreshing: Boolean that indicates if the update-station should stop refreshing the packages.
        total_packages: Integer that indicates the total number of packages that are that will be updated.
        update_started: Boolean that indicates if the application has started updating the system.
    """
    backup: bool = False
    close_session: bool = False
    current_abi: str = ''
    do_not_upgrade: bool = False
    kernel_upgrade: bool = False
    major_upgrade: bool = False
    new_abi: str = ''
    packages_dictionary: dict = {}
    second_update: bool = False
    stop_pkg_refreshing: bool = False
    total_packages: int = 0
    update_started: bool = False