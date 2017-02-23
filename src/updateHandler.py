#!/usr/local/bin/python

"""All fuction to handle various update for GhostBSD."""

from os import listdir, path
from subprocess import Popen, PIPE, STDOUT, call
# import urllib
import platform

ustation_db = '/var/db/update-station/'
distroDesktop = "/usr/local/etc/default/distro"
pkglockfile = '%slock-pkgs' % ustation_db
pkglist = '/var/db/pkg-update-check/pkg-update-list'
fbsduf = '/var/db/freebsd-update-check/'
pkgupdatefile = ustation_db + 'pkg-to-upgrade'
fbtag = '%stag' % fbsduf
fblist = '%stag' % fbsduf
fbvcmd = "freebsd-version"
fblist = '%stag' % fbsduf
arch = platform.uname()[4]
desktop = open(distroDesktop, "r").readlines()[0].rstrip().partition("=")[2]
checkfbsdupdate = 'doas fbsdupdatecheck check'
fetchfbsdupdate = 'doas fbsdupdatecheck fetch'
installfbsdupdate = 'doas fbsdupdatecheck install'
checkpkgupgrade = 'doas fbsdpkgupdate check'
fetchpkgupgrade = 'doas pkg upgrade -Fy'
isntallpkgupgrade = 'doas pkg upgrade -y'
lockpkg = 'doas pkg lock -y '
unlockallpkg = 'doas pkg unlock -ay'
unlockpkg = 'doas pkg unlock -y '

release = Popen('uname -r', shell=True, stdin=PIPE, stdout=PIPE,
                stderr=STDOUT, close_fds=True).stdout.readlines()[0].rstrip()
if not path.isdir(ustation_db):
    Popen('doas mkdir -p ' + ustation_db, shell=True, close_fds=True)
    Popen('doas chmod -R 665 ' + ustation_db, shell=True, close_fds=True)
fbftp = "ftp://ftp.freebsd.org/pub/"

fbsrcurl = fbftp + "FreeBSD/releases/%s/%s/%s/src.txz" % (arch, arch, release)
extractsrc = "doas tar Jxvf src.txz -C /"
cleandotdesktop = "doas sh /usr/local/lib/update-station/cleandesktop.sh"


def dowloadsrc():
    fetch = Popen('fetch %s' % fbsrcurl, shell=True, stdout=PIPE,
                  close_fds=True)
    return fetch.stdout


def installsrc():
    extract = Popen(extractsrc, shell=True, stdout=PIPE, close_fds=True)
    return extract.stdout


def listofinstal():
    ls = listdir(fbsduf)
    for line in ls:
        if 'install.' in line:
            uptag = open(fbsduf + line + '/INDEX-NEW', 'r')
            info = uptag.readlines()
            return info


def checkfreebsdupdate():
    fbsdinstall = Popen(checkfbsdupdate, shell=True, stdin=PIPE, stdout=PIPE,
                        stderr=STDOUT, close_fds=True)
    if "updating to" in fbsdinstall.stdout.read():
        return True
    else:
        return False


def checkversionupdate():
    if path.exists(fbtag):
        uptag = open(fbtag, 'r')
        tag = uptag.readlines()[0].rstrip().split('|')
        upversion = tag[2] + "-p" + tag[3]
        fbv = Popen(fbvcmd, shell=True, stdin=PIPE, stdout=PIPE,
                    stderr=STDOUT, close_fds=True)
        fbsdversion = fbv.stdout.readlines()[0].rstrip()
        if "p0" in upversion:
            return False
        elif fbsdversion == upversion:
            return False
        else:
            return True
    else:
        return False


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


def fetchfreebsdupdate():
    fbsddownload = Popen(fetchfbsdupdate, shell=True, stdout=PIPE,
                         close_fds=True)
    return fbsddownload.stdout


def installfreebsdupdate():
    fbsdinstall = Popen(installfbsdupdate, shell=True, stdout=PIPE,
                        close_fds=True)
    return fbsdinstall.stdout


def checkpkgupdate():
    call(checkpkgupgrade, shell=True, stdout=PIPE, close_fds=True)
    return True


def runcheckupdate():
    checkfreebsdupdate()
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
    fetch = Popen(fetchpkgupgrade, shell=True, stdout=PIPE, close_fds=True)
    return fetch.stdout


def installpkgupdate():
    install = Popen(isntallpkgupgrade, shell=True, stdout=PIPE, close_fds=True)
    return install.stdout


def checkforupdate():
    if checkversionupdate() is True or checkpkgupdatefromfile() is True:
        return True
    else:
        return False


def cleandesktop():
    call(cleandotdesktop, shell=True)
    return True
