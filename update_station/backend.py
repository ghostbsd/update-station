#!/usr/local/bin/python
"""All functions to handle various command for Update Station."""

import os
import re
import sys
import socket
import requests
import bectl
import datetime
from gi.repository import Gtk
from update_station.data import Data
from subprocess import Popen, PIPE, call, run, CompletedProcess

lib_path: str = f'{sys.prefix}/lib/update-station'
update_station_db: str = '/var/db/update-station'
pkg_lock_file: str = f'{update_station_db}/lock-pkgs'
updates_run: str = '/tmp/update-station'


def read_file(file_path: str) -> str:
    """
    Read a file and return the contents.
    :param file_path: The file path.
    :return: The file contents.
    """
    with open(file_path, 'r') as file:
        return file.read()


def on_reboot(*args) -> None:
    """
    The function to reboot the system.
    """
    Popen(['shutdown', '-r', 'now'])
    Gtk.main_quit()


def get_detail(*args) -> None:
    """
    Get the details of the upgrade failure.
    :return:
    """
    Popen(['sudo', '-u', Data.username, 'xdg-open', f'{Data.home}/update.failed'])


def build_env(env: dict = None) -> dict:
    """
    Build the environment for a command from the current environment.

    :param env: Optional environment variables added on top of the current environment.

    :return: The environment dictionary, or None to inherit the current environment as is.
    """
    return {**os.environ, **env} if env else None


def run_command(command: list, check: bool = False, env: dict = None) -> CompletedProcess:
    """
    Run a command and optionally check for errors.

    :param command: The command and its arguments as a list.
    :param check: Optional parameter to check for errors.
    :param env: Optional environment variables added on top of the current environment.

    :return: The CompletedProcess object.
    """
    process = run(command, stdout=PIPE, stderr=PIPE, universal_newlines=True, env=build_env(env), check=False)
    if check and process.returncode != 0:
        raise RuntimeError(f"Command failed: {' '.join(command)}\n{process.stderr}")
    return process


def command_output(command: list, env: dict = None) -> Popen:
    """
    Run command and return the live Popen process.

    :param command: The command and its arguments as a list.
    :param env: Optional environment variables added on top of the current environment.

    :return: The Popen process object.
    """
    return Popen(
        command,
        stdout=PIPE,
        stderr=PIPE,
        close_fds=True,
        universal_newlines=True,
        env=build_env(env)
    )


def check_for_update() -> bool | None:
    """
    Check if there is an update.

    :return: True if there is an update, False if there is none, None if the repository
             catalogue could not be refreshed and the answer cannot be trusted.
    """
    if not update_repository():
        return None
    upgrade_text = get_pkg_upgrade()
    return 'Your packages are up to date' not in upgrade_text and (
        'UPGRADED:' in upgrade_text or 'DOWNGRADED:' in upgrade_text
    )


def find_updates() -> bool | None:
    """
    Look for updates and set the upgrade type from the versions found.

    The repository of the running system is checked first because its package updates must
    be installed before a major upgrade. A pending major upgrade is therefore put aside
    while looking, and only restored when there is nothing else to install first.

    :return: True if there is something to upgrade, False if there is nothing, None if the
             repository could not be read and the upgrade type is therefore unknown.
    """
    major_upgrade = Data.upgrade_type == 'major'
    Data.upgrade_type = 'none'
    update_available = check_for_update()
    if update_available is None:
        return None
    if update_available:
        Data.current_version = get_current_version()
        Data.new_version = get_version()
        Data.upgrade_type = classify_upgrade(Data.current_version, Data.new_version)
        return True
    if major_upgrade:
        Data.upgrade_type = 'major'
        update_available = check_for_update()
        if update_available is None:
            Data.upgrade_type = 'none'
            return None
        if update_available:
            # Read the versions again now that the catalogue of the new ABI has been fetched.
            # The ones stored when the major upgrade was detected come from the old catalogue,
            # and they name the boot environment the upgrade is installed in.
            Data.current_version = get_current_version()
            Data.new_version = get_version(Data.new_abi)
            if not Data.new_version:
                # The boot environment of the upgrade is named after this version, and it
                # cannot be created without one.
                Data.upgrade_type = 'none'
                return None
            return True
        Data.upgrade_type = 'none'
    return False


def get_enabled_repo_url(repo_type: str, abi: str = None) -> str:
    """
    Get the URL of the first enabled repository of the given type from pkg -vv.

    :param repo_type: The last path component of the repository URL ("latest" or "base").
    :param abi: Optional ABI string (e.g., "FreeBSD:15:amd64"). If None, uses the current ABI.

    :return: The repository URL.
    """
    env = {'ABI': abi} if abi else None
    output = run_command(['pkg', '-vv'], env=env).stdout
    url = ''
    for line in output.splitlines():
        if match := re.search(rf'url\s*:\s*"(https://pkg\.[^"]+/{repo_type})"', line):
            url = match[1]
        elif re.search(r'enabled\s*:\s*yes', line) and url:
            return url
        elif line.strip() == '}':
            url = ''
    return ''


def get_default_repo_url() -> str:
    """
    Get the default pkg repository url.

    :return: The default pkg repository url.
    """
    return get_enabled_repo_url('latest')


def get_default_base_repo_url(abi: str = None) -> str:
    """
    Get the base repository URL, optionally for a specific ABI.

    :param abi: Optional ABI string (e.g., "FreeBSD:15:amd64"). If None, uses the current ABI.

    :return: The base repository URL (GhostBSD-base repository).
    """
    return get_enabled_repo_url('base', abi)


def get_abi_upgrade() -> str:
    """
    Get the major upgrade version.

    :return: The major upgrade version.

    Output:
        - FreeBSD:14:amd64
        - FreeBSD:15:amd64
    """
    next_version = f'{get_default_repo_url()}/.next_version'
    return requests.get(next_version).text.strip()


def get_current_abi() -> str:
    """
    Get the current ABI of the system.

    :return: The current ABI of the system.
    """
    return run_command(['pkg', 'config', 'ABI']).stdout.strip()


def get_current_version() -> str:
    """
    Get the full GhostBSD version currently installed on the system.

    :return: The full version string (e.g., "25.02-R14.3p8").
    """
    result = run_command(['ghostbsd-version'])
    return result.stdout.strip()


def get_version(new_abi: str = None) -> str:
    """
    Get the full GhostBSD version available in the repository.

    pkg rquery exits non-zero both when the query fails and when the repository simply has no
    such package, so the two cannot be told apart and an empty string covers both.

    :param new_abi: Optional new ABI string (e.g., "FreeBSD:15:amd64"). If None, uses the current ABI.

    :return: The full version string (e.g., "25.02-R14.3p8"), or an empty string on failure.
    """
    env = {'ABI': new_abi, 'IGNORE_OSVERSION': 'yes'} if new_abi else None
    result = run_command(['pkg', 'rquery', '%v', 'GhostBSD-runtime'], env=env)
    if result.returncode != 0:
        return ''
    return result.stdout.strip()


def get_installed_version() -> str:
    """
    Get the GhostBSD version of the installed GhostBSD-runtime package.

    :return: The full version string (e.g., "26.1-R15.0p13"), or an empty string on failure.
    """
    result = run_command(['pkg', 'query', '%v', 'GhostBSD-runtime'])
    if result.returncode != 0:
        return ''
    return result.stdout.strip()


def parse_version(version: str) -> tuple:
    """
    Parse a GhostBSD version string into its numeric components.

    :param version: The version string (e.g., "26.1-R15.0p13", "26.2-R15.1b1").

    :return: A tuple of (ghostbsd_major, ghostbsd_minor, freebsd_major, freebsd_minor),
             or an empty tuple if the string does not match the expected format.
    """
    match = re.fullmatch(r'(\d+)\.(\d+)-R(\d+)\.(\d+)(?:(?:a|b|rc|p)\d+)?', version.strip())
    if not match:
        return ()
    return tuple(int(group) for group in match.groups())


def classify_upgrade(installed: str, remote: str) -> str:
    """
    Classify the upgrade between the installed and the repository GhostBSD version.

    Major upgrades (FreeBSD ABI change) are detected separately through .next_version,
    so this only distinguishes upgrades served by the current ABI repository.

    :param installed: The installed version string (e.g., "26.1-R15.0p13").
    :param remote: The repository version string (e.g., "26.2-R15.1p2").

    :return: 'minor' if the FreeBSD minor version changes, 'release' if only the
             GhostBSD release changes, or 'none' for patch level and package updates.
    """
    installed_parts = parse_version(installed)
    remote_parts = parse_version(remote)
    if not installed_parts or not remote_parts or remote_parts <= installed_parts:
        return 'none'
    if remote_parts[2:] != installed_parts[2:]:
        return 'minor'
    if remote_parts[:2] != installed_parts[:2]:
        return 'release'
    return 'none'


def fetch_base_packagelist(new_abi: str = None) -> list:
    """
    Fetch the base package list from the repository.

    :param new_abi: Optional new ABI string (e.g., "FreeBSD:15:amd64"). If None, uses the current ABI.

    :return: List of base package names.
    """
    base_repo_url = get_default_base_repo_url(new_abi)
    url = f'{base_repo_url}/packagelist.json'
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    return response.json()


def cleanup_old_backups(keep_count: int = 5) -> None:
    """
    Clean old auto_backup BEs, keeping only the most recent ones by timestamp.

    :param keep_count: Number of auto_backup BEs to keep.
    """
    be_list = bectl.get_be_list()
    auto_backups = [be for be in be_list if 'auto_backup' in be]

    if len(auto_backups) <= keep_count:
        return

    # Sort by timestamp in BE name (format: version-auto_backup-YYYY-MM-DD_HHmmss)
    # Extract timestamp after 'auto_backup-' and sort by it (newest first)
    auto_backups.sort(key=lambda be: be.split()[0].split('auto_backup-')[-1], reverse=True)
    backups_to_delete = auto_backups[keep_count:]

    for be_line in backups_to_delete:
        columns = be_line.split()
        if len(columns) < 4:
            continue
        be_name = columns[0]
        active_status = columns[1]
        mount_point = columns[2]
        if 'N' in active_status and mount_point == '/':
            continue
        if 'R' in active_status:
            continue
        bectl.destroy_be(be_name)


def create_be(full_version: str, upgrade: bool = False) -> str:
    """
    Create a boot environment.

    :param full_version: The complete version string (e.g., "25.02-R14.3p8").
    :param upgrade: If True, creates a boot environment for a system upgrade.

    :return: The boot environment name.
    """
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H%M%S")
    backup = '' if upgrade else '-auto_backup'
    be_name = f'{full_version}{backup}-{timestamp}'
    bectl.create_be(new_be_name=be_name)
    return be_name


def mount_be(be_name: str) -> str:
    """
    Mount the boot environment.

    :param be_name: The boot environment name.

    :return: The mount path of the boot environment.
    """
    return bectl.mount_be(be_name)


def bootstrap_pkg_in_be(mount_path: str, new_abi: str = None) -> Popen:
    """
    Bootstrap pkg in the mounted boot environment.

    :param mount_path: The mount path of the boot environment.
    :param new_abi: Optional new ABI string (e.g., "FreeBSD:15:amd64"). If None, uses the current ABI.

    :return: The Popen process object for live output streaming.
    """
    env = {'ASSUME_ALWAYS_YES': 'yes'}
    if new_abi:
        env.update({'ABI': new_abi, 'IGNORE_OSVERSION': 'yes'})
    return command_output(['pkg-static', '-r', mount_path, 'bootstrap', '-f'], env=env)


def upgrade_packages_in_be(mount_path: str, fetch_only: bool, force: bool, new_abi: str = None,
                           package_list: list = None) -> Popen:
    """
    Fetch or install package upgrades in the mounted boot environment.

    :param mount_path: The mount path of the boot environment.
    :param fetch_only: If True, only fetch the packages without installing them.
    :param force: If True, reinstall packages even if they are already up to date.
    :param new_abi: Optional new ABI string (e.g., "FreeBSD:15:amd64"). If None, uses the current ABI.
    :param package_list: Optional list of package names. If empty, upgrades all packages.

    :return: The Popen process object for live output streaming.
    """
    env = {'ABI': new_abi} if new_abi else None
    option = '-Fy' if fetch_only else '-y'
    if force:
        option += 'f'
    command = ['pkg-static', '-r', mount_path, 'upgrade', option] + (package_list or [])
    return command_output(command, env=env)


def fetch_base_packages_in_be(mount_path: str, package_list: list, new_abi: str = None,
                              force: bool = False) -> Popen:
    """
    Fetch base packages in the mounted boot environment.

    :param mount_path: The mount path of the boot environment.
    :param package_list: List of base package names to fetch.
    :param new_abi: Optional new ABI string (e.g., "FreeBSD:15:amd64"). If None, uses the current ABI.
    :param force: If True, fetch packages even if they are already up to date.

    :return: The Popen process object for live output streaming.
    """
    return upgrade_packages_in_be(mount_path, True, force, new_abi, package_list)


def fetch_software_packages_in_be(mount_path: str, new_abi: str = None, force: bool = False) -> Popen:
    """
    Fetch all remaining software packages in the mounted boot environment.

    :param mount_path: The mount path of the boot environment.
    :param new_abi: Optional new ABI string (e.g., "FreeBSD:15:amd64"). If None, uses the current ABI.
    :param force: If True, fetch packages even if they are already up to date.

    :return: The Popen process object for live output streaming.
    """
    return upgrade_packages_in_be(mount_path, True, force, new_abi)


def upgrade_base_packages_in_be(mount_path: str, package_list: list, new_abi: str = None,
                                force: bool = False) -> Popen:
    """
    Install base packages in the mounted boot environment.

    :param mount_path: The mount path of the boot environment.
    :param package_list: List of base package names to upgrade.
    :param new_abi: Optional new ABI string (e.g., "FreeBSD:15:amd64"). If None, uses the current ABI.
    :param force: If True, reinstall packages even if they are already up to date.

    :return: The Popen process object for live output streaming.
    """
    return upgrade_packages_in_be(mount_path, False, force, new_abi, package_list)


def upgrade_software_packages_in_be(mount_path: str, new_abi: str = None, force: bool = False) -> Popen:
    """
    Install all remaining software packages in the mounted boot environment.

    :param mount_path: The mount path of the boot environment.
    :param new_abi: Optional new ABI string (e.g., "FreeBSD:15:amd64"). If None, uses the current ABI.
    :param force: If True, reinstall packages even if they are already up to date.

    :return: The Popen process object for live output streaming.
    """
    return upgrade_packages_in_be(mount_path, False, force, new_abi)


def umount_upgrade_be(be_name: str) -> None:
    """
    Unmount the boot environment.

    :param be_name: The boot environment name.
    """
    bectl.umount_be(be_name)


def activate_upgrade_be(be_name: str) -> None:
    """
    Activate the boot environment for next boot.

    :param be_name: The boot environment name.
    """
    bectl.activate_be(be_name)


def cleanup_failed_upgrade_be(be_name: str) -> None:
    """
    Clean up a failed boot environment upgrade.

    :param be_name: The boot environment name.
    """
    bectl.umount_be(be_name)
    bectl.destroy_be(be_name)


def reboot_is_pending() -> bool:
    """
    Check if a boot environment other than the running one is activated for the next boot.

    An upgrade installed in a boot environment only takes effect on reboot, and until then the
    running system still reports the version it had before, so looking for updates would find
    and install the very same upgrade a second time.

    :return: True if the system has to reboot before looking for updates again else False.
    """
    if not bectl.is_file_system_zfs():
        return False
    for be_line in bectl.get_be_list():
        columns = be_line.split()
        if len(columns) < 2:
            continue
        # 'N' is the running boot environment and 'R' the one for the next boot, so 'NR' is a
        # system that boots into what it already runs and needs no reboot.
        if 'R' in columns[1] and 'N' not in columns[1]:
            return True
    return False


def get_pkg_upgrade(option: str = '') -> str:
    """
    Get the upgrade data from pkg.
    :param option: f to get full upgrade data, n to get only the new packages data.

    :return:  The upgrade data.
    """
    env = {'ABI': Data.new_abi} if Data.upgrade_type == 'major' else None
    return run_command(['pkg', 'upgrade', f'-n{option}'], env=env).stdout


def get_packages_list_by_upgrade_type(upgrade_type: str, update_pkg: str, update_pkg_list: list) -> list:
    """
    Get the list of packages by the upgrade type.
    :param upgrade_type: The upgrade type: REMOVED, UPGRADED, INSTALLED, REINSTALLED, DOWNGRADED.
    :param update_pkg: The upgrade data.
    :param update_pkg_list: The list of the upgrade data.
    :return: The list of packages.
    """
    package_list = []
    stop = False
    if f'{upgrade_type}:' in update_pkg:
        for line in update_pkg_list:
            if f'{upgrade_type}:' in line:
                stop = True
            elif stop is True and line == '':
                break
            elif stop is True:
                package_list.append(line.strip())
    return package_list


def get_pkg_upgrade_data() -> dict:
    """
    This function is used to get the upgrade data from pkg.
    :return: Returns a dictionary with the following keys:
        - remove: The list of packages to remove.
        - number_to_remove: The number of packages to remove.
        - upgrade: The list of packages to upgrade.
        - number_to_upgrade: The number of packages to upgrade.
        - upgrade: The list of packages to upgrade.
        - number_to_upgrade: The number of packages to upgrade.
        - install: The list of packages to install.
        - number_to_install: The number of packages to install.
        - reinstall: The list of packages to reinstall.
        - number_to_reinstall: The number of packages to reinstall.
        - total_of_packages: The total number of packages to upgrade.
    """
    option = 'f' if Data.force_reinstall() else ''
    update_pkg = get_pkg_upgrade(option)
    update_pkg_list = update_pkg.splitlines()
    pkg_to_upgrade = get_packages_list_by_upgrade_type(
        'UPGRADED', update_pkg, update_pkg_list
    )
    pkg_to_downgrade = get_packages_list_by_upgrade_type(
        'DOWNGRADED', update_pkg, update_pkg_list
    )
    pkg_to_install = get_packages_list_by_upgrade_type(
        ' INSTALLED', update_pkg, update_pkg_list
    )
    pkg_to_reinstall = get_packages_list_by_upgrade_type(
        'REINSTALLED', update_pkg, update_pkg_list
    )
    pkg_to_remove = get_packages_list_by_upgrade_type(
        'REMOVED', update_pkg, update_pkg_list
    )
    total_of_packages = len(pkg_to_upgrade)
    total_of_packages += (len(pkg_to_downgrade)
                          + len(pkg_to_install)
                          + len(pkg_to_reinstall)
                          + len(pkg_to_remove))
    return {
        'upgrade': pkg_to_upgrade,
        'number_to_upgrade': len(pkg_to_upgrade),
        'downgrade': pkg_to_downgrade,
        'number_to_downgrade': len(pkg_to_downgrade),
        'install': pkg_to_install,
        'number_to_install': len(pkg_to_install),
        'reinstall': pkg_to_reinstall,
        'number_to_reinstall': len(pkg_to_reinstall),
        'remove': pkg_to_remove,
        'number_to_remove': len(pkg_to_remove),
        'total_of_packages': (
            len(pkg_to_upgrade)
            + len(pkg_to_downgrade)
            + len(pkg_to_install)
            + len(pkg_to_reinstall)
            + len(pkg_to_remove)
        )
    }


def is_major_upgrade_available() -> bool:
    """
    Check if the major upgrade is ready.
    :return: True if the major upgrade is ready else False.
    """
    next_version = f'{get_default_repo_url()}/.next_version'
    try:
        response = requests.get(next_version, timeout=5)
        return response.status_code == 200
    except requests.RequestException:
        # If we cannot reach the server or the request fails,
        # treat it as "no upgrade available" to avoid blocking UI flows.
        return False


def update_repository() -> bool:
    """
    Update the repository catalogue of the pending upgrade.

    This must run before reading the upgrade list or querying the repository version,
    otherwise pkg answers from a stale catalogue.

    :return: True if the catalogue was refreshed, False if pkg could not refresh it.
    """
    env = {'ASSUME_ALWAYS_YES': 'yes'}
    if Data.upgrade_type == 'major':
        env['ABI'] = Data.new_abi
    return run_command(['pkg', 'update', '-f'], env=env).returncode == 0


def lock_pkg(lock_pkg_list: list) -> None:
    """
    Lock all packages in the list.
    :param lock_pkg_list: The list of pkg to lock.
    """
    for line in lock_pkg_list:
        call(['pkg', 'lock', '-y', line.strip()])


def look_update_station() -> None:
    """
    Create a lock file to prevent multiple update at the same time.
    """
    if not os.path.exists(updates_run):
        os.mkdir(updates_run)
    open(f'{updates_run}/updating', 'w').close()


def network_stat() -> str:
    """
    Check if the network is up.
    :return: UP if the network is up else DOWN.
    """
    routes = run_command(['netstat', '-rn'])
    return "UP" if 'default' in routes.stdout else 'DOWN'


def repo_online() -> bool:
    """
    Check if the repository is online.
    """
    server = list(filter(None, get_default_repo_url().split('/')))[1]
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(5)
        s.connect((server, 80))
    except OSError:
        return False
    else:
        s.close()
        return True


def repository_is_syncing() -> bool:
    """
    Check if the repository is syncing.
    :return: True if the repository is syncing else False.
    """
    syncing_url = f'{get_default_repo_url()}/.syncing'
    try:
        response = requests.get(syncing_url, timeout=5)
        return response.status_code == 200
    except requests.RequestException:
        # If we cannot reach the server, treat it as "not syncing"
        # to avoid blocking update checks.
        return False


def unlock_all_pkg() -> None:
    """
    Unlock all locked packages.
    """
    call(['pkg', 'unlock', '-ay'])


def unlock_pkg(lock_pkg_list: list) -> None:
    """
    Unlock all packages in the list.
    :param lock_pkg_list: The list of pkg to unlock.
    """
    for line in lock_pkg_list:
        call(['pkg', 'unlock', '-y', line.strip()])


def unlock_update_station() -> None:
    """
    Remove the lock file.
    """
    os.remove(f'{updates_run}/updating')


def updating() -> bool:
    """
    Check if the system is updating.
    :return: True if the system is updating else False.
    """
    return bool(os.path.exists(f'{updates_run}/updating'))


# the code below is for upgrading to PKGBASE this will be removed in the future.
def find_if_os_generic_exists() -> bool:
    """
    This function is look if there is some os generic packages installed.
    :return: True if some os generic packages are exists else False.
    """
    return run_command(['pkg', 'info', '-E', '-g', 'os-generic*']).returncode == 0


def set_package_base_config_file() -> CompletedProcess:
    # /usr/local/etc/pkg/repos/GhostBSD.conf
    config_path = '/usr/local/etc/pkg/repos/GhostBSD.conf'
    return run_command(['cp', f'{config_path}.default', config_path])


def remove_os_generic(mount_point: str) -> CompletedProcess:
    """
    This function is used to remove all os generic packages.
    :param mount_point: The mount point of the basepkg-test.
    """
    return run_command(['pkg-static', '-r', mount_point, 'delete', '-yf', '-g', 'os-generic*'])


def install_ghostbsd_pkgbase(mount_point: str) -> CompletedProcess:
    """
    This function is used to install the GhostBSD-base package.
    :param mount_point: The mount point of the basepkg-test.
    """
    return run_command(['pkg-static', '-r', mount_point, 'install', '-y', '-r', 'GhostBSD-base', '-g', 'GhostBSD-*'])


def fetch_ghostbsd_pkgbase(mount_point: str) -> CompletedProcess:
    """
    This function is used to download the GhostBSD-base package.
    :param mount_point: The mount point of the basepkg-test.
    """
    return run_command(['pkg-static', '-r', mount_point, 'fetch', '-y', '-r', 'GhostBSD-base', '-g', 'GhostBSD-*'])


def restore_vital_files(mount_point: str) -> None:
    """
    This function is used to restart the vital files.
    :param mount_point: The mount point of the basepkg-test.
    """
    run_command(['cp', '/etc/passwd', f'{mount_point}/etc/passwd'])
    run_command(['cp', '/etc/master.passwd', f'{mount_point}/etc/master.passwd'])
    run_command(['cp', '/etc/group', f'{mount_point}/etc/group'])
    run_command(['cp', '/etc/sysctl.conf', f'{mount_point}/etc/sysctl.conf'])
    run_command(['mkdir', f'{mount_point}/proc'])
    run_command(['chroot', mount_point, 'pwd_mkdb', '-p', '/etc/master.passwd'])


def remove_package_config() -> CompletedProcess:
    """
    This function is used to remove the package config file.
    :return: The CompletedProcess object.
    """
    config_path = '/usr/local/etc/pkg/repos/GhostBSD.conf'
    return run_command(['rm', config_path])
