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
checkpkgupgrade = 'sudo operator fbsdpkgupdate check'
fetchpkgupgrade = 'sudo operator pkg upgrade -Fy'
isntallpkgupgrade = 'sudo operator pkg upgrade -y'
lockpkg = 'sudo operator pkg lock -y '
unlockallpkg = 'sudo operator pkg unlock -ay'
unlockpkg = 'sudo operator pkg unlock -y '

release = Popen('uname -r', shell=True, stdin=PIPE, stdout=PIPE,
                stderr=STDOUT, close_fds=True).stdout.readlines()[0].rstrip()
if not path.isdir(ustation_db):
    Popen('sudo operator mkdir -p ' + ustation_db, shell=True, close_fds=True)
    Popen('sudo operator chmod -R 665 ' + ustation_db, shell=True,
          close_fds=True)
    Popen('sudo operator chown root:wheel ' + ustation_db, shell=True,
          close_fds=True)

fbsrcurl = "ftp://ftp.freebsd.org/pub/FreeBSD/releases/%s/%s/%s/src.txz" % (arch, arch, release)

fetchsrc = "sudo operator fetch %s" % fbsrcurl
extractsrc = "sudo operator tar Jxvf src.txz -C /"
fetchports = "sudo operator portsnap fetch"
extractports = "sudo operator portsnap extract"
updateports = "sudo operator portsnap update"
cleandesktop = "sudo operator sh /usr/local/lib/update-station/cleandesktop.sh"
gbupdatelist = ustation_db + "update-list.txt"
ghostbsdUpdate = "ftp://ghostbsd.org/pub/GhostBSD/update/" + arch + "/" + desktop + "/update-list.txt " + "-o " + ustation_db + "update-list.txt"


def dowloadSrc():
    fetch = Popen('fetch %s' % fbsrcurl, shell=True, stdout=PIPE,
                  close_fds=True)
    return fetch.stdout


def installSrc():
    extract = Popen(extractsrc, shell=True, stdout=PIPE, close_fds=True)
    return extract.stdout


def portsFetch():
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
    if "No updates needed." in fetch.stdout.read():
        return False
    else:
        return True


def ifPortsIstall():
    if path.isdir('/usr/ports') is True:
        return True
    else:
        return False


def listOfInstal():
    ls = listdir(fbsduf)
    for line in ls:
        if 'install.' in line:
            uptag = open(fbsduf + line + '/INDEX-NEW', 'r')
            info = uptag.readlines()
            return info


# GhostBSD port update on GitHub.
def fetchGBportslist():
    call("sudo operator fetch " + ghostbsdUpdate, shell=True, stdout=PIPE,
         close_fds=True)
    call('sudo operator chmod -R 766 ' + gbupdatelist, shell=True,
         close_fds=True)


def lookGBupdate():
    # upgb = open(gbupdatelist, 'r')
    upgb = Popen("sudo operator cat " + gbupdatelist, shell=True, stdout=PIPE,
                 close_fds=True)
    needupdate = False
    for ports in upgb.stdout.readlines():
        nprtlist = ports.rstrip().split()
        nprtsname = nprtlist[0]
        print nprtsname
        nprtversion = nprtlist[1]
        portsub = Popen("pkg query '%n %v'| grep " + nprtsname,
                        shell=True, stdout=PIPE, close_fds=True)
        oldport = portsub.stdout.readlines()[0].rstrip()
        if oldport != "":
            prtversion = oldport.split()[1]
            print nprtversion + ">" + prtversion
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

print lookGBupdate()


def downloadGBPorts():
    download = 'sudo operator git clone https://github.com/ghostbsd/ports.git /tmp/ports'
    gbsddownload = Popen(download, shell=True, stdout=PIPE, close_fds=True)
    return gbsddownload.stdout


def copyGBport():
    copy = "sudo operator cp -Rfv /tmp/ports/ /usr/ports"
    gbcopyPorts = Popen(copy, shell=True, stdout=PIPE, close_fds=True)
    return gbcopyPorts.stdout


def deleteGBport():
    delete = "sudo operator rm -rf /tmp/ports"
    gbdeletePorts = Popen(delete, shell=True, stdout=PIPE, close_fds=True)
    return gbdeletePorts.stdout


def installGBUpdate():
    upgb = Popen("sudo operator cat " + gbupdatelist, shell=True, stdout=PIPE,
                 close_fds=True)
    for ports in upgb.stdout.readlines():
        nprtlist = ports.rstrip().split()
        nprtsname = nprtlist[0]
        nprtversion = nprtlist[1]
        pkgquery = Popen("sudo operator pkg query '%n %v'| grep " + nprtsname,
                         shell=True, stdout=PIPE, close_fds=True)
        pkglist = pkgquery.readlines()[0].rstrip().split()
        prtversion = pkglist[1]
        if float(prtversion) < float(nprtversion):
            findport = "find /usr/ports/ -name " + nprtsname
            portdir = Popen(findport, shell=True, stdout=PIPE, close_fds=True)
            chdir(portdir.stdout.readlines()[0].rstrip())
            call("sudo operator make reinstall clean", shell=True, stdout=PIPE,
                 close_fds=True)


def checkFreeBSDUpdate():
    check = 'sudo operator fbsdupdatecheck check'
    fbsdinstall = Popen(check, shell=True, stdin=PIPE, stdout=PIPE,
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
    download = 'sudo operator fbsdupdatecheck fetch'
    fbsddownload = Popen(download, shell=True, stdout=PIPE, close_fds=True)
    return fbsddownload.stdout


def installFreeBSDUpdate():
    install = 'sudo operator fbsdupdatecheck install'
    fbsdinstall = Popen(install, shell=True, stdout=PIPE, close_fds=True)
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
    if checkVersionUpdate() is True or CheckPkgUpdateFromFile() is True or lookGBupdate() is True:
        return True
    else:
        return False


def cleanDesktop():
    call(cleandesktop, shell=True)
    return True
