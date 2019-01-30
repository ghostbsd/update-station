#!/usr/local/bin/python

"""All fuction to handle various update for GhostBSD."""

from os import listdir, path
from subprocess import Popen, PIPE, STDOUT, call
# import urllib
import platform

ustation_db = '/var/db/update-station/'
pkglockfile = '%slock-pkgs' % ustation_db
pkglist = '/var/db/pkg-update-check/pkg-update-list'
fbsduf = '/var/db/freebsd-update-check/'
pkgupdatefile = ustation_db + 'pkg-to-upgrade'
fbtag = '%stag' % fbsduf
fblist = '%stag' % fbsduf
fbvcmd = "freebsd-version"
fblist = '%stag' % fbsduf
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
    Popen('mkdir -p ' + ustation_db, shell=True, close_fds=True)
    Popen('chmod -R 665 ' + ustation_db, shell=True, close_fds=True)

fbftp = "ftp://ftp.freebsd.org/pub/"
fbsrcurl = fbftp + "FreeBSD/releases/%s/%s/%s/src.txz" % (arch, arch, release)
cleandotdesktop = "sh /usr/local/lib/update-station/cleandesktop.sh"


def listofinstal():
    ls = listdir(fbsduf)
    for line in ls:
        if 'install.' in line:
            uptag = open(fbsduf + line + '/INDEX-NEW', 'r')
            info = uptag.readlines()
            return info


def lookfbsdupdate():
    if path.exists(fbtag):
        uptag = open(fbtag, 'r')
        tag = uptag.readlines()[0].rstrip().split('|')
        return "FreeBSD Update: " + tag[2] + "-p" + tag[3]
    else:
        return None


def updatetext():
    udatetitle = lookfbsdupdate()
    text = "Update Details:\n"
    text += "%s\n\n" % udatetitle
    text += "The following files will be update:\n"
    for line in listofinstal():
        txtlist = line.split('|')
        text += "%s" % txtlist[0] + "\n"
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
    if "UPGRADED:" in uptag.read():
        return True
    else:
        return False


def pkgupdatelist():
    uppkg = open(pkglist, 'r')
    pkgarr = []
    for line in uppkg.readlines():
        if "->" in line:
            pkgarr.append(line.rstrip()[1:])
    return pkgarr


def lockpkg(pkglist):
    for line in pkglist:
        call(pkglist + line.rstrip(), shell=True)
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
    if checkpkgupdatefromfile() is True:
        return True
    else:
        return False
