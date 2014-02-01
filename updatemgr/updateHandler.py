#!/usr/local/bin/python

import os
from subprocess import Popen, PIPE, STDOUT, call
fetch = "freebsd-update cron"
fbtag = '/var/db/freebsd-update/tag'
updatemgrtag = '/var/db/updatemgr/tag'
fbvcmd = "freebsd-version"
installfbupdate = "freebsd-update install"


def listOfInstal():
    ls = os.listdir('/var/db/freebsd-update')
    for line in ls:
        if 'install' in line:
            print True
        else:
            print False

listOfInstal()


def chmodfu():
    call('chmod 755 /var/db/freebsd-update', shell=True)


def checkUpdate():
    if os.path.exists(fbtag):
        call('chmod 755 /var/db/freebsd-update', shell=True)
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


def lookUpdate():
    if os.path.exists(fbtag):
        call('chmod 755 /var/db/freebsd-update', shell=True)
        uptag = open(fbtag, 'r')
        tag = uptag.readlines()[0].rstrip().split('|')
        return "FreeBSD " + tag[2] + "-p" + tag[3] + " system update"

def updateText():
    udatetitle = lookUpdate()
