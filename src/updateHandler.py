#!/usr/local/bin/python
"""All functions to handle various updates for GhostBSD."""

import os
import socket
import requests
from subprocess import Popen, PIPE, call, run

ustation_db = '/var/db/update-station'
pkg_lock_file = f'{ustation_db}/lock-pkgs'
updates_run = '/tmp/update-station'


def check_for_update() -> bool:
    """
    Check if there is an update.
    :return: True if there is an update else False.
    """
    kernel_version_change()
    upgrade_text = get_pkg_upgrade('')
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
        'pkg -vv | grep -B 1 "enabled.*yes" | grep url',
        shell=True,
        stdout=PIPE,
        close_fds=True,
        universal_newlines=True,
        encoding='utf-8'
    )
    pkg_url = raw_url.stdout.read().strip().split('"')[1]
    return pkg_url


def get_major_upgrade_version() -> str:
    """
    Get the major upgrade version.
    :return: The major upgrade version.

    Output:
        - FreeBSD:14:amd64
        - FreeBSD:15:amd64
    """
    next_version = f'{get_default_repo_url()}/.next_version'
    return requests.get(next_version).json()


def get_pkg_upgrade(option: str) -> str:
    """
    Get the upgrade data from pkg.
    :param option: f to get full upgrade data, n to get only the new packages data.
    :return:  The upgrade data.
    """
    pkg_upgrade = Popen(
        f'pkg upgrade -n{option}',
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
    if kernel_version_change():
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
    pkg_update = Popen(
        'yes | pkg update -f',
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
    cmd = "pkg -vv | grep -B 1 'enabled.*yes' | grep url"
    raw_url = Popen(
        cmd,
        shell=True,
        stdout=PIPE,
        close_fds=True,
        universal_newlines=True,
        encoding='utf-8'
    )
    server = list(filter(None, raw_url.stdout.read().split('/')))[1]
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
