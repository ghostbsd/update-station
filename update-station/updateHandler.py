#!/usr/local/bin/python

from os import listdir, path
from subprocess import Popen, PIPE, STDOUT

fbsduf = '/var/db/freebsd-update-check/'
fbtag = '%stag' % fbsduf
fblist = '%stag' % fbsduf
fbvcmd = "freebsd-version"
installfbupdate = "freebsd-update fetch install"
fblist = '%stag' % fbsduf
fbsduf = '/var/db/freebsd-update-check/'
pulcmd = 'pkg upgrade -n'


def listOfInstal():
    ls = listdir(fbsduf)
    for line in ls:
        if 'install.' in line:
            uptag = open(fbsduf + line + '/INDEX-NEW', 'r')
            info = uptag.readlines()
            return info


def checkFbsdUpdate():
    if path.exists(fbtag):
        uptag = open(fbtag, 'r')
        tag = uptag.readlines()[0].rstrip().split('|')
        upversion = tag[2] + "-p" + tag[3]
        fbv = Popen(fbvcmd, shell=True, stdin=PIPE, stdout=PIPE,
        stderr=STDOUT, close_fds=True)
        fbsdversion = fbv.stdout.readlines()[0].rstrip()
        if fbsdversion == upversion:
            return False
        else:
            return True


def lookFbsdUpdate():
    if path.exists(fbtag):
        uptag = open(fbtag, 'r')
        tag = uptag.readlines()[0].rstrip().split('|')
        return "FreeBSD Update:" + tag[2] + "-p" + tag[3]
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


def pkg_update():
    fbv = Popen('%s | grep -v upgrade | grep -v package' % pulcmd,
    shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT, close_fds=True)
    print((fbv.stdout.read()))


#pkg_update()