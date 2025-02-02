#!/usr/local/bin/python
"""All functions to handle various command for Update Station."""

import os
import sys
import socket
import requests
from gi.repository import Gtk
from update_station.data import Data
from subprocess import Popen, PIPE, run, CompletedProcess

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
    update_local_pkg_database()
    upgrade_text = get_pkg_upgrade()
    if 'Your packages are up to date' in upgrade_text:
        return False
    elif 'UPGRADED:' in upgrade_text:
        return True
    elif 'INSTALLED:' in upgrade_text:
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


def get_pkg_upgrade() -> str:
    """
    This function is used to get the upgrade data from pkg.

    :return: This function returns the pkg upgrade output.
    """
    env = f'env ABI={Data.new_abi} ' if Data.major_upgrade else ''
    pkg_upgrade = Popen(
        f'{env}pkg upgrade -n',
        shell=True,
        stdout=PIPE,
        close_fds=True,
        universal_newlines=True,
        encoding='utf-8'
    )
    return pkg_upgrade.stdout.read()


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
    update_pkg = get_pkg_upgrade()
    update_pkg_list = update_pkg.splitlines()
    system_upgrade = False
    if 'kernel-generic' in update_pkg:
        Data.system_upgrade = True
        system_upgrade = True
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
        'number_to_remove': len(pkg_to_remove),
        'upgrade': pkg_to_upgrade,
        'number_to_upgrade': len(pkg_to_upgrade),
        'install': pkg_to_install,
        'number_to_install': len(pkg_to_install),
        'reinstall': pkg_to_reinstall,
        'number_to_reinstall': len(pkg_to_reinstall),
        'total_of_packages': len(pkg_to_remove) + len(pkg_to_upgrade) + len(pkg_to_install) + len(pkg_to_reinstall)
    }
    return pkg_dictionary


def is_major_upgrade_available() -> bool:
    """
    Check if the major upgrade is ready.
    :return: True if the major upgrade is ready else False.
    """
    next_version = f'{get_default_repo_url()}/.next_version'
    return True if requests.get(next_version).status_code == 200 else False


def update_local_pkg_database() -> None:
    """
    Check if the kernel version has changed.
    :return: True if the kernel version has changed else False.
    """
    env = f'env ABI={Data.new_abi} ' if Data.major_upgrade else ''
    run(
        f'yes | {env}pkg update -f',
        shell=True,
        stdout=PIPE,
        close_fds=True,
        universal_newlines=True,
        encoding='utf-8'
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
