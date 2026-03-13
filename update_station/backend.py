#!/usr/local/bin/python
"""All functions to handle various command for Update Station."""

import os
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
    Popen('shutdown -r now', shell=True)
    Gtk.main_quit()


def get_detail(*args) -> None:
    """
    Get the details of the upgrade failure.
    :return:
    """
    Popen(f'sudo -u {Data.username} xdg-open {Data.home}/update.failed', shell=True)


def run_command(command: str, check: bool = False) -> CompletedProcess:
    """
    Run a shell command and optionally check for errors.

    :param command: The shell command to run.
    :param check: Optional parameter to check for errors.

    :return: The CompletedProcess object.
    """
    process = run(command, shell=True, stdout=PIPE, stderr=PIPE, universal_newlines=True)
    if check and process.returncode != 0:
        raise RuntimeError(f"Command failed: {command}\n{process.stderr}")
    return process


def command_output(command: str) -> Popen:
    """
    Run command and return the live Popen process.

    :param command: The shell command to run.
    
    :return: The Popen process object.
    """
    return Popen(
        command,
        shell=True,
        stdout=PIPE,
        stderr=PIPE,
        close_fds=True,
        universal_newlines=True
    )


def check_for_update() -> bool:
    """
    Check if there is an update.
    
    :return: True if there is an update else False.
    """
    kernel_version_change()
    upgrade_text = get_pkg_upgrade()
    return 'Your packages are up to date' not in upgrade_text and (
        'UPGRADED:' in upgrade_text or 'DOWNGRADED:' in upgrade_text
    )


def get_default_repo_url() -> str:
    """
    Get the default pkg repository url.

    :return: The default pkg repository url.
    """
    raw_url = Popen(
        'pkg -vv | grep -B 1 "enabled.*yes" | grep url | grep latest',
        shell=True,
        stdout=PIPE,
        close_fds=True,
        universal_newlines=True,
        encoding='utf-8'
    )
    return raw_url.stdout.read().strip().split('"')[1]


def get_default_base_repo_url(abi: str = '') -> str:
    """
    Get the base repository URL, optionally for a specific ABI.

    :param abi: Optional ABI string (e.g., "FreeBSD:15:amd64"). If empty, uses current ABI.

    :return: The base repository URL (GhostBSD-base repository).
    """
    env = f'env ABI={abi} ' if abi else ''
    raw_url = Popen(
        f'{env}pkg -vv | grep -B 1 "enabled.*yes" | grep url | grep base',
        shell=True,
        stdout=PIPE,
        close_fds=True,
        universal_newlines=True,
        encoding='utf-8'
    )
    return raw_url.stdout.read().strip().split('"')[1]


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
    pkg_abi = Popen(
        'pkg -vv | grep ABI | grep -v ALTABI | cut -d\'"\' -f2',
        shell=True,
        stdout=PIPE,
        close_fds=True,
        universal_newlines=True,
        encoding='utf-8'
    )
    return pkg_abi.stdout.read().strip()


def get_current_version() -> str:
    """
    Get the full GhostBSD version currently installed on the system.

    :return: The full version string (e.g., "25.02-R14.3p8").
    """
    result = run_command('ghostbsd-version')
    return result.stdout.strip()


def get_version(new_abi: str) -> str:
    """
    Get the full GhostBSD version from the new ABI repository.

    :param new_abi: The new ABI string (e.g., "FreeBSD:15:amd64").

    :return: The full version string (e.g., "25.02-R14.3p8").
    """
    result = run_command(f'env ABI={new_abi} IGNORE_OSVERSION=yes pkg rquery "%v" GhostBSD-runtime')
    return result.stdout.strip()


def fetch_base_packagelist(new_abi: str) -> list:
    """
    Fetch the base package list from the repository.

    :param new_abi: The new ABI string (e.g., "FreeBSD:15:amd64").

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
    :param upgrade: If True, creates a boot environment for a major upgrade.

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


def bootstrap_pkg_in_be(mount_path: str, new_abi: str) -> Popen:
    """
    Bootstrap pkg in the mounted boot environment.

    :param mount_path: The mount path of the boot environment.
    :param new_abi: The new ABI string (e.g., "FreeBSD:15:amd64").

    :return: The Popen process object for live output streaming.
    """
    command = f'env ABI={new_abi} IGNORE_OSVERSION=yes ASSUME_ALWAYS_YES=yes pkg-static -r {mount_path} bootstrap -f'
    return command_output(command)


def fetch_base_packages_in_be(mount_path: str, new_abi: str, package_list: list) -> Popen:
    """
    Fetch base packages in the mounted boot environment.

    :param mount_path: The mount path of the boot environment.
    :param new_abi: The new ABI string (e.g., "FreeBSD:15:amd64").
    :param package_list: List of base package names to fetch.

    :return: The Popen process object for live output streaming.
    """
    env = f'env ABI={new_abi} ' if new_abi else ''
    packages = ' '.join(package_list)
    command = f'{env}pkg-static -r {mount_path} upgrade -Fy {packages}'
    return command_output(command)


def fetch_software_packages_in_be(mount_path: str, new_abi: str = '') -> Popen:
    """
    Fetch all remaining software packages in the mounted boot environment.

    :param mount_path: The mount path of the boot environment.
    :param new_abi: Optional new ABI string (e.g., "FreeBSD:15:amd64"). If empty, uses current ABI.

    :return: The Popen process object for live output streaming.
    """
    env = f'env ABI={new_abi} ' if new_abi else ''
    command = f'{env}pkg-static -r {mount_path} upgrade -Fy'
    return command_output(command)


def upgrade_base_packages_in_be(mount_path: str, new_abi: str, package_list: list) -> Popen:
    """
    Install base packages in the mounted boot environment.

    :param mount_path: The mount path of the boot environment.
    :param new_abi: The new ABI string (e.g., "FreeBSD:15:amd64").
    :param package_list: List of base package names to upgrade.

    :return: The Popen process object for live output streaming.
    """
    env = f'env ABI={new_abi} ' if new_abi else ''
    packages = ' '.join(package_list)
    command = f'{env}pkg-static -r {mount_path} upgrade -y {packages}'
    return command_output(command)


def upgrade_software_packages_in_be(mount_path: str, new_abi: str = '') -> Popen:
    """
    Install all remaining software packages in the mounted boot environment.

    :param mount_path: The mount path of the boot environment.
    :param new_abi: Optional new ABI string (e.g., "FreeBSD:15:amd64"). If empty, uses current ABI.

    :return: The Popen process object for live output streaming.
    """
    env = f'env ABI={new_abi} ' if new_abi else ''
    command = f'{env}pkg-static -r {mount_path} upgrade -y'
    return command_output(command)


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


def get_pkg_upgrade(option: str = '') -> str:
    """
    Get the upgrade data from pkg.
    :param option: f to get full upgrade data, n to get only the new packages data.
    
    :return:  The upgrade data.
    """

    env = f'env ABI={Data.new_abi} ' if Data.major_upgrade else ''
    print(f'{env}pkg upgrade -n{option}')
    pkg_upgrade = Popen(
        f'{env}pkg upgrade -n{option}',
        shell=True,
        stdout=PIPE,
        close_fds=True,
        universal_newlines=True,
        encoding='utf-8'
    )
    return pkg_upgrade.stdout.read()


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
        - system_upgrade: True if the system is upgrading else False.
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
    option = ''
    system_upgrade = False
    if kernel_version_change() or Data.major_upgrade:
        Data.kernel_upgrade = True
        system_upgrade = True
        option = 'f'
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
        'system_upgrade': system_upgrade,
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


def kernel_version_change() -> bool:
    """
    Check if the kernel version has changed.
    :return: True if the kernel version has changed else False.
    """
    env = f'env ABI={Data.new_abi} ' if Data.major_upgrade else ''
    print(f'yes | {env}pkg update -f')
    pkg_update = Popen(
        f'yes | {env}pkg update -f',
        shell=True,
        stdout=PIPE,
        close_fds=True,
        universal_newlines=True,
        encoding='utf-8'
    )
    return 'Newer FreeBSD version' in pkg_update.stdout.read()


def lock_pkg(lock_pkg_list: list) -> None:
    """
    Lock all packages in the list.
    :param lock_pkg_list: The list of pkg to lock.
    """
    for line in lock_pkg_list:
        call(
            f'pkg lock -y {line.strip()}',
            shell=True
        )


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
    cmd = "netstat -rn | grep default"
    netstat = run(cmd, shell=True)
    return "UP" if netstat.returncode == 0 else 'DOWN'


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
    call(
        'pkg unlock -ay',
        shell=True
    )


def unlock_pkg(lock_pkg_list: list) -> None:
    """
    Unlock all packages in the list.
    :param lock_pkg_list: The list of pkg to unlock.
    """
    for line in lock_pkg_list:
        call(
            f'pkg unlock -y {line.strip()}',
            shell=True
        )


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
    return run_command("pkg info -E -g 'os-generic*'").returncode == 0


def set_package_base_config_file() -> CompletedProcess:
    # /usr/local/etc/pkg/repos/GhostBSD.conf
    config_path = '/usr/local/etc/pkg/repos/GhostBSD.conf'
    return run_command(f'cp {config_path}.default {config_path}')


def remove_os_generic(mount_point: str) -> CompletedProcess:
    """
    This function is used to remove all os generic packages.
    :param mount_point: The mount point of the basepkg-test.
    """
    return run_command(f'pkg-static -r {mount_point} delete -yf -g "os-generic*"')


def install_ghostbsd_pkgbase(mount_point: str) -> CompletedProcess:
    """
    This function is used to install the GhostBSD-base package.
    :param mount_point: The mount point of the basepkg-test.
    """
    return run_command(f'pkg-static -r {mount_point} install -y -r GhostBSD-base -g "GhostBSD-*"')


def fetch_ghostbsd_pkgbase(mount_point: str) -> CompletedProcess:
    """
    This function is used to download the GhostBSD-base package.
    :param mount_point: The mount point of the basepkg-test.
    """
    return run_command(f'pkg-static -r {mount_point} fetch -y -r GhostBSD-base -g "GhostBSD-*"')


def restore_vital_files(mount_point: str) -> None:
    """
    This function is used to restart the vital files.
    :param mount_point: The mount point of the basepkg-test.
    """
    run_command(f'cp /etc/passwd {mount_point}/etc/passwd')
    run_command(f'cp /etc/master.passwd {mount_point}/etc/master.passwd')
    run_command(f'cp /etc/group {mount_point}/etc/group')
    run_command(f'cp /etc/sysctl.conf {mount_point}/etc/sysctl.conf')
    run_command(f'mkdir {mount_point}/proc')
    run_command(f'chroot {mount_point} pwd_mkdb -p /etc/master.passwd')


def remove_package_config() -> CompletedProcess:
    """
    This function is used to remove the package config file.
    :return: The CompletedProcess object.
    """
    config_path = '/usr/local/etc/pkg/repos/GhostBSD.conf'
    return run_command(f'rm {config_path}')
