#!/usr/local/bin/python
"""All functions to handle various updates for GhostBSD."""

from subprocess import Popen, PIPE, call

ustation_db = '/var/db/update-station'
pkg_lock_file = f'{ustation_db}/lock-pkgs'


def get_pkg_upgrade(option):
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


def kerenel_verstion_change():
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


def get_pkg_upgrade_data():
    option = ''
    system_upgrade = False
    if kerenel_verstion_change():
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
                stop = False
                break
            elif stop is True:
                pkg_to_reinstall.append(line.strip())
    pkg_dictionaire = {
        'system_upgrade': system_upgrade,
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


def check_for_update():
    option = ''
    # make sure to update database first with kerenel_verstion_change
    kerenel_verstion_change()
    upgrade_text = get_pkg_upgrade(option)
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
