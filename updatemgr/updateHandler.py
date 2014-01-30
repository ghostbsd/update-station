#!/usr/local/bin/python

import os
from subprocess import Popen, PIPE, STDOUT, call
fetch = "freebsd-update cron"
fbtag = '/var/db/freebsd-update/tag'
updatemgrtag = '/var/db/updatemgr/tag'

def checkUpdate():
    if os.path.exists(fbtag):
        uptag = open(fbtag, 'r')
        taglist = uptag.readlines()[0].rstrip().split('|')
        print(taglist)
        return True
    else:
        return False


class lookUpdate():

    def __init__(self):
        if os.path.exists(fbtag):
            uptag = open(fbtag, 'r')
            taglist = uptag.readlines()[0].rstrip().split('|')
            print(taglist)

print checkUpdate()