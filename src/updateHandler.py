#!/usr/local/bin/python

"""All fuction to handle various update for GhostBSD."""

from os import listdir, path, chdir
from subprocess import Popen, PIPE, STDOUT, call
# import urllib
import platform

ustation_db = '/var/db/update-station/'
disroDesktop = "/usr/local/etc/default/distro"
pkglockfile = '%slock-pkgs' % ustation_db
pkglist = '/var/db/pkg-update-check/pkg-update-list'
fbsduf = '/var/db/freebsd-update-check/'
pkgupdatefile = ustation_db + 'pkg-to-upgrade'
fbtag = '%stag' % fbsduf
fblist = '%stag' % fbsduf
fbvcmd = "freebsd-version"
fblist = '%stag' % fbsduf
arch = platform.uname()[4]
desktop = open(disroDesktop, "r").readlines()[0].rstrip()
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
fetchports = "doas portsnap fetch"
extractports = "doas portsnap extract"
updateports = "doas portsnap update"
cleandesktop = "doas sh /usr/local/lib/update-station/cleandesktop.sh"
gbupdatelist = ustation_db + "update-list.txt"
gbftp = "ftp://ghostbsd.org/pub/GhostBSD/"
gbud = gbftp + "update/" + arch + "/" + desktop + "/update-list.txt"
fetchgbupdate = "doas fetch " + gbud + " -o " + gbupdatelist
portspath = "/usr/ports"
catgbul = "doas cat " + gbupdatelist
copygbport = "doas cp -Rfv /tmp/ports/ /usr/ports"


def dowloadsrc():
    fetch = Popen('fetch %s' % fbsrcurl, shell=True, stdout=PIPE,
                  close_fds=True)
    return fetch.stdout


def installsrc():
    extract = Popen(extractsrc, shell=True, stdout=PIPE, close_fds=True)
    return extract.stdout


def portsfetch():
    fetch = Popen(fetchports, shell=True, stdout=PIPE, close_fds=True)
    return fetch.stdout


def portsExtract():
    extract = Popen(extractports, shell=True, stdout=PIPE, close_fds=True)
    return extract.stdout


def portsUpdate():
    update = Popen(updateports, shell=True, stdout=PIPE, close_fds=True)
    return update.stdout


def IfPortsUpdated():
    fetch = Popen(fetchports, shell=True, stdout=PIPE, close_fds=True)
    portsmsg = fetch.stdout.read()
    if "No updates needed" in portsmsg or "Fetching 0" in portsmsg:
        return False
    else:
        return True


def ifPortsInstall():
    if not path.isdir(portspath):
        return False
    elif not listdir(portspath):
        return False
    else:
        return True


def listOfInstal():
    ls = listdir(fbsduf)
    for line in ls:
        if 'install.' in line:
            uptag = open(fbsduf + line + '/INDEX-NEW', 'r')
            info = uptag.readlines()
            return info


# GhostBSD port update on GitHub.
def fetchGBportslist():
    call(fetchgbupdate, shell=True, stdout=PIPE, close_fds=True)


def lookGBupdate():
    # upgb = open(gbupdatelist, 'r')
    upgb = Popen(catgbul, shell=True, stdout=PIPE,
                 close_fds=True)
    needupdate = False
    for ports in upgb.stdout.readlines():
        nprtlist = ports.rstrip().split()
        nprtsname = nprtlist[0]
        nprtversion = nprtlist[1]
        portsub = Popen("pkg query '%n %v'| grep " + nprtsname,
                        shell=True, stdout=PIPE, close_fds=True)
        oldport = portsub.stdout.readlines()[0].rstrip()
        if oldport != "":
            prtversion = oldport.split()[1]
            if nprtversion > prtversion:
                needupdate = True
                break
        else:
            needupdate = True
            break
    if needupdate is True:
        return True
    else:
        return False


def downloadGBPorts():
    download = 'git clone https://github.com/ghostbsd/ports.git /tmp/ports'
    gbsddownload = Popen(download, shell=True, stdout=PIPE, close_fds=True)
    return gbsddownload.stdout


def copyGBport():
    gbcopyports = Popen(copygbport, shell=True, stdout=PIPE, close_fds=True)
    return gbcopyports.stdout


def deleteGBport():
    delete = "rm -rf /tmp/ports"
    gbdeleteports = Popen(delete, shell=True, stdout=PIPE, close_fds=True)
    return gbdeleteports.stdout


def installGBUpdate():
    upgb = Popen(catgbul, shell=True, stdout=PIPE,
                 close_fds=True)
    for ports in upgb.stdout.readlines():
        nprtlist = ports.rstrip().split()
        nprtsname = nprtlist[0]
        nprtversion = nprtlist[1]
        pkgquery = Popen("pkg query '%n %v'| grep " + nprtsname,
                         shell=True, stdout=PIPE, close_fds=True)
        pkglist = pkgquery.readlines()[0].rstrip().split()
        prtversion = pkglist[1]
        if float(prtversion) < float(nprtversion):
            findport = "find /usr/ports/ -name " + nprtsname
            portdir = Popen(findport, shell=True, stdout=PIPE, close_fds=True)
            chdir(portdir.stdout.readlines()[0].rstrip())
            call("doas make reinstall clean", shell=True, stdout=PIPE,
                 close_fds=True)


def checkFreeBSDUpdate():
    fbsdinstall = Popen(checkfbsdupdate, shell=True, stdin=PIPE, stdout=PIPE,
                        stderr=STDOUT, close_fds=True)
    if "updating to" in fbsdinstall.stdout.read():
        return True
    else:
        return False


def checkVersionUpdate():
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


def lookFbsdUpdate():
    if path.exists(fbtag):
        uptag = open(fbtag, 'r')
        tag = uptag.readlines()[0].rstrip().split('|')
        return "FreeBSD Update: " + tag[2] + "-p" + tag[3]
    else:
        return None


def updateText():
    udatetitle = lookFbsdUpdate()
    text = "Update Details:\n"
    text += "%s\n\n" % udatetitle
    text += "The following files will be update:\n"
    for line in listOfInstal():
        txtlist = line.split('|')
        text += "%s" % txtlist[0] + "\n"
    return text


def fetchFreeBSDUpdate():
    fbsddownload = Popen(fetchfbsdupdate, shell=True, stdout=PIPE,
                         close_fds=True)
    return fbsddownload.stdout


def installFreeBSDUpdate():
    fbsdinstall = Popen(installfbsdupdate, shell=True, stdout=PIPE,
                        close_fds=True)
    return fbsdinstall.stdout


def checkPkgUpdate():
    call(checkpkgupgrade, shell=True, stdout=PIPE, close_fds=True)
    return True


def runCheckUpdate():
    checkFreeBSDUpdate()
    checkPkgUpdate()
    fetchGBportslist()
    return True


def CheckPkgUpdateFromFile():
    uptag = open(pkglist, 'r')
    if "UPGRADED:" in uptag.read():
        return True
    else:
        return False


def pkgUpdateList():
    uppkg = open(pkglist, 'r')
    pkgarr = []
    for line in uppkg.readlines():
        if "->" in line:
            pkgarr.append(line.rstrip()[1:])
    return pkgarr


def lockPkg(lockPkg):
    for line in lockPkg:
        call(lockpkg + line.rstrip(), shell=True)
    return True


def unlockPkg():
    # unlock all pkg
    call(unlockpkg, shell=True)
    return True


def fetchPkgUpdate():
    fetch = Popen(fetchpkgupgrade, shell=True, stdout=PIPE, close_fds=True)
    return fetch.stdout


def installPkgUpdate():
    install = Popen(isntallpkgupgrade, shell=True, stdout=PIPE, close_fds=True)
    return install.stdout


def checkForUpdate():
    # if checkVersionUpdate() is True or CheckPkgUpdateFromFile() is True or lookGBupdate() is True or IfPortsUpdated() is True or ifPortsInstall() is False:
    if checkVersionUpdate() is True or CheckPkgUpdateFromFile() is True or lookGBupdate() is True or ifPortsInstall() is False:

        return True
    else:
        return False


def cleanDesktop():
    call(cleandesktop, shell=True)
    return True
