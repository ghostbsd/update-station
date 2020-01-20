#!/usr/local/bin/python

"""All function to handle various update for GhostBSD."""

from os import listdir, path
from subprocess import Popen, PIPE, STDOUT, call
# import urllib
import platform

ustation_db = '/var/db/update-station/'
pkglockfile = f'{ustation_db}lock-pkgs'
pkglist = '/var/db/pkg-update-check/pkg-update-list'
fbsduf = '/var/db/freebsd-update-check/'
pkgupdatefile = f'{ustation_db}pkg-to-upgrade'
fbtag = f'{fbsduf}tag'
fblist = f'{fbsduf}tag'
fbvcmd = 'freebsd-version'
fblist = f'{fbsduf}tag'
arch = platform.uname()[4]
checkfbsdupdate = 'fbsdupdatecheck check'
fetchfbsdupdate = 'fbsdupdatecheck fetch'
installfbsdupdate = 'fbsdupdatecheck install'
checkpkgupgrade = 'fbsdpkgupdate check'
fetchpkgupgrade = 'pkg upgrade -Fy'
isntallpkgupgrade = 'pkg upgrade -y'
lockpkg = 'pkg lock -y '
unlockallpkg = 'pkg unlock -ay'
unlockpkg = 'pkg unlock -y '

release = Popen('uname -r', shell=True, stdin=PIPE, stdout=PIPE,
                stderr=STDOUT, close_fds=True
                ).stdout.readlines()[0].rstrip()

if not path.isdir(ustation_db):
    Popen(f'mkdir -p {ustation_db}', shell=True, close_fds=True)
    Popen(f'chmod -R 665 {ustation_db}', shell=True, close_fds=True)

fbftp = 'ftp://ftp.freebsd.org/pub/'
fbsrcurl = f'{fbftp}FreeBSD/releases/{arch}/{arch}/{release}/src.txz'
cleandotdesktop = 'sh /usr/local/lib/update-station/cleandesktop.sh'


def listofinstal():
    ls = listdir(fbsduf)
    for line in ls:
        if 'install.' in line:
            uptag = open(f'{fbsduf}{line}/INDEX-NEW', 'r')
            info = uptag.readlines()
            return info


def lookfbsdupdate():
    if path.exists(fbtag):
        uptag = open(fbtag, 'r')
        tag = uptag.readlines()[0].rstrip().split('|')
        return f'FreeBSD Update: {tag[2]}-p{tag[3]}'
    else:
        return None


def updatetext():
    udatetitle = lookfbsdupdate()
    text = 'Update Details:\n'
    text += f'{udatetitle}\n\n'
    text += 'The following files will be update:\n'
    for line in listofinstal():
        txtlist = line.split('|')
        text += f'{txtlist[0]}\n'
    return text


def checkpkgupdate():
    call(checkpkgupgrade, shell=True, stdout=PIPE, close_fds=True,
         universal_newlines=True)
    return True


def runcheckupdate():
    checkpkgupdate()
    return True


def checkpkgupdatefromfile():
    uptag = open(pkglist, 'r')
    return 'UPGRADED:' in uptag.read()

def pkgupdatelist():
    uppkg = open(pkglist, 'r')
    pkgarr = []
    for line in uppkg.readlines():
        if '->' in line:
            pkgarr.append(line.rstrip()[1:])
    return pkgarr


def lockpkg(pkglist):
    for line in pkglist:
        call(f'{pkglist}{line.rstrip()}', shell=True)
    return True


def unlockpkg():
    # unlock all pkg
    call(unlockpkg, shell=True)
    return True


def fetchpkgupdate():
    fetch = Popen(fetchpkgupgrade, shell=True, stdout=PIPE, close_fds=True,
                  universal_newlines=True)
    return fetch.stdout


def installpkgupdate():
    install = Popen(isntallpkgupgrade, shell=True, stdout=PIPE, close_fds=True,
                    universal_newlines=True)
    return install.stdout


def checkforupdate():
    return checkpkgupdatefromfile()
