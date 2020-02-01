#!/usr/local/bin/python
"""All fuction to handle various update for GhostBSD."""

from subprocess import Popen, PIPE, call

ustation_db = '/var/db/update-station'
pkg_lock_file = f'{ustation_db}/lock-pkgs'


def get_pkg_upgrade():
    pkg_upgrade = Popen(
        'pkg upgrade -n',
        shell=True,
        stdout=PIPE,
        close_fds=True,
        universal_newlines=True,
        encoding='utf-8'
    )
    upgrade_verbose = pkg_upgrade.stdout.read()
    return upgrade_verbose


def get_pkg_upgrade_data():
    update_pkg = get_pkg_upgrade()
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
                stop = False
                break
            elif stop is True:
                pkg_to_reinstall.append(line.strip())
    pkg_dictionaire = {
        'remove': pkg_to_remove,
        'upgrade': pkg_to_upgrade,
        'install': pkg_to_install,
        'reinstall': pkg_to_reinstall
    }
    return pkg_dictionaire


def lock_pkg(Lock_pkg_list):
    for line in Lock_pkg_list:
        call(
            f'pkg lock -y {line.strip()}',
            shell=True
        )
    return True


def unlock_all_pkg():
    call(
        'pkg unlock -ay',
        shell=True
    )
    return True


def unlock_pkg(Lock_pkg_list):
    for line in Lock_pkg_list:
        call(
            f'pkg unlock -y {line.strip()}',
            shell=True
        )
    return True


def fetch_pkg_update():
    fetch = Popen(
        'pkg upgrade -Fy',
        shell=True,
        stdout=PIPE,
        close_fds=True,
        universal_newlines=True
    )
    return fetch.stdout


def install_pkg_update():
    install = Popen(
        'pkg upgrade -y',
        shell=True,
        stdout=PIPE,
        close_fds=True,
        universal_newlines=True
    )
    return install.stdout


def check_for_update():
    if 'Your packages are up to date' in get_pkg_upgrade():
        return False
    else:
        return True
