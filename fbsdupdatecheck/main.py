#!/usr/local/bin/python

from os import system
from sys import argv

if len(argv) == 2: 
    if argv[1] != "update":
        print("Invalid option!")
    else:
        # Fetch to the standard working-dir
        system("touch /tmp/.fbsdup-lock")
        system("cat /usr/sbin/freebsd-update | sed 's|! -t 0|-z '1'|g' | /bin/sh -s 'fetch'")
        system("rm /tmp/.fbsdup-lock")
else:
    system("touch /tmp/.fbsdup-lock")
    system("mkdir /var/db/freebsd-update-check 2>/dev/null")
    system("cat /usr/sbin/freebsd-update | sed 's|! -t 0|-z '1'|g' | /bin/sh -s 'fetch' '-d' '/var/db/freebsd-update-check'")
    system("chmod 755 /var/db/freebsd-update-check")
    system("chmod 755 /var/db/freebsd-update-check/*")
    system("rm /tmp/.fbsdup-lock")


