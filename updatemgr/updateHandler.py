#!/usr/local/bin/python

from os import listdir, system, path
from subprocess import Popen, PIPE, STDOUT, call

fbsduf = '/var/db/freebsd-update-check/'
fbtag = '%stag' % fbsduf
fblist = '%stag' % fbsduf
fbvcmd = "freebsd-version"
installfbupdate = "freebsd-update fetch install"
fblist = '%stag' % fbsduf
fbsduf = '/var/db/freebsd-update-check/'


def listOfInstal():
    ls = listdir(fbsd_up_file)
    for line in ls:
        if 'install.' in line:
            uptag = open(fbsd_up_file + line + '/INDEX-NEW', 'r')
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
            return True
        else:
            return False


def lookFbsdUpdate():
    if path.exists(fbtag):
        uptag = open(fbtag, 'r')
        tag = uptag.readlines()[0].rstrip().split('|')
        return "Update to FreeBSD " + tag[2] + "-p" + tag[3]
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
