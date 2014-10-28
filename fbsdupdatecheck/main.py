#!/usr/local/bin/python

from os import system
from sys import argv

if len(argv) == 2:
    if argv[1] == "install":
        system("touch /tmp/.fbsdup-lock")
        system("cat /usr/sbin/freebsd-update | sed 's|! -t 0|-z '1'|g' | /bin/sh -s 'fetch'")
        system("rm /tmp/.fbsdup-lock")
    elif argv[1] == "install":
        system("touch /tmp/.fbsdup-lock")
        system("cat /usr/sbin/freebsd-update | sed 's|! -t 0|-z '1'|g' | /bin/sh -s 'install'")
        system("rm /tmp/.fbsdup-lock")
    elif argv[1] == "check":
        system("touch /tmp/.fbsdup-lock")
        system("mkdir /var/db/freebsd-update-check 2>/dev/null")
        system("cat /usr/sbin/freebsd-update | sed 's|! -t 0|-z '1'|g' | /bin/sh -s 'fetch' '-d' '/var/db/freebsd-update-check'")
        system("chmod 755 /var/db/freebsd-update-check")
        system("chmod 755 /var/db/freebsd-update-check/*")
        system("rm /tmp/.fbsdup-lock")
    elif argv[1] != "check" and argv[1] != "install":
        print((argv[1] + " is an invalid option!"))
else:
    system("touch /tmp/.fbsdup-lock")
    system("mkdir /var/db/freebsd-update-check 2>/dev/null")
    system("cat /usr/sbin/freebsd-update | sed 's|! -t 0|-z '1'|g' | /bin/sh -s 'fetch' '-d' '/var/db/freebsd-update-check'")
    system("chmod 755 /var/db/freebsd-update-check")
    system("chmod 755 /var/db/freebsd-update-check/*")
    system("rm /tmp/.fbsdup-lock")