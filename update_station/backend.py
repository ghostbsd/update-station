#!/usr/local/bin/python
"""All functions to handle various command for Update Station."""

import os
import sys
import socket
import requests
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


def get_detail() -> None:
    """
    Get the details of the upgrade failure.
    :return:
    """
    Popen(f'sudo -u {Data.username} xdg-open {Data.home}/update.failed', shell=True)


def get_packages_to_reinstall() -> list:
    """
    Get packages to reinstall on kernel upgrade.
    :return: The list of packages to reinstall.
    """
    packages = read_file(f'../src/pkg_to_reinstall').replace('\n', ' ')
    return run_command(f'pkg query "%n" {packages}').stdout.splitlines()


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


def check_for_update() -> bool:
    """
    Check if there is an update.
    :return: True if there is an update else False.
    """
    kernel_version_change()
    upgrade_text = get_pkg_upgrade()
    if 'Your packages are up to date' in upgrade_text:
        return False
    elif 'UPGRADED:' in upgrade_text:
        return True
    elif ' INSTALLED:' in upgrade_text:
        return True
    elif 'REINSTALLED:' in upgrade_text:
        return True
    elif 'REMOVED:' in upgrade_text:
        return True
    else:
        return False


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
    pkg_url = raw_url.stdout.read().strip().split('"')[1]
    return pkg_url


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
    upgrade_verbose = pkg_upgrade.stdout.read()
    return upgrade_verbose


def get_pkg_upgrade_data() -> dict:
    """
    Get the upgrade data from pkg.
    :return: The upgrade data.
    """
    option = ''
    system_upgrade = False
    if kernel_version_change() or Data.major_upgrade:
        Data.kernel_upgrade = True
        system_upgrade = True
        option = 'f'
    update_pkg = get_pkg_upgrade(option)
    update_pkg_list = update_pkg.splitlines()
    pkg_to_remove = []
    pkg_to_upgrade = []
    pkg_to_install = []
    pkg_to_reinstall = []
    stop = False
    if 'REMOVED:' in update_pkg:
        for line in update_pkg_list:
            if 'REMOVED:' in line:
                stop = True
            elif stop is True and line == '':
                stop = False
                break
            elif stop is True:
                pkg_to_remove.append(line.strip())
    if 'UPGRADED:' in update_pkg:
        for line in update_pkg_list:
            if 'UPGRADED:' in line:
                stop = True
            elif stop is True and line == '':
                stop = False
                break
            elif stop is True:
                pkg_to_upgrade.append(line.strip())
    if ' INSTALLED:' in update_pkg:
        for line in update_pkg_list:
            if ' INSTALLED:' in line:
                stop = True
            elif stop is True and line == '':
                stop = False
                break
            elif stop is True:
                pkg_to_install.append(line.strip())
    if 'REINSTALLED:' in update_pkg:
        for line in update_pkg_list:
            if 'REINSTALLED:' in line:
                stop = True
            elif stop is True and line == '':
                break
            elif stop is True:
                pkg_to_reinstall.append(line.strip())
    pkg_dictionary = {
        'system_upgrade': system_upgrade,
        'remove': pkg_to_remove,
        'upgrade': pkg_to_upgrade,
        'install': pkg_to_install,
        'reinstall': pkg_to_reinstall
    }
    return pkg_dictionary


def is_major_upgrade_available() -> bool:
    """
    Check if the major upgrade is ready.
    :return: True if the major upgrade is ready else False.
    """
    next_version = f'{get_default_repo_url()}/.next_version'
    return True if requests.get(next_version).status_code == 200 else False


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
    if 'Newer FreeBSD version' in pkg_update.stdout.read():
        return True
    else:
        return False


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
    return True if requests.get(syncing_url).status_code == 200 else False


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
    if os.path.exists(f'{updates_run}/updating'):
        return True
    else:
        return False


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
