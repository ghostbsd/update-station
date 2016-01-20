#!/usr/bin/env python

from os import system
from sys import argv

checkpkgupgrade = 'pkg upgrade -n'
fetchpkgupgrade = 'pkg upgrade -Fy'
isntallpkgupgrade = 'pkg upgrade -y'

if len(argv) == 2:
    if argv[1] == "fetch":
        system(fetchpkgupgrade)
    elif argv[1] == "install" or argv[1] == "update" or argv[1] == "upgrade":
        system(isntallpkgupgrade)
    elif argv[1] == "check":
        system("mkdir /var/db/pkg-update-check 2>/dev/null")
        system(checkpkgupgrade + " > /var/db/pkg-update-check/pkg-update-list")
        system("chmod 755 /var/db/pkg-update-check")
        system("chmod 755 /var/db/pkg-update-check/*")
    elif argv[1] != "check" and argv[1] != "install":
        print((argv[1] + " is an invalid option!"))
else:
    system("mkdir /var/db/pkg-update-check 2>/dev/null")
    system( checkpkgupgrade + " > /var/db/pkg-update-check/pkg-update-list")
    system("chmod 755 /var/db/pkg-update-check")
    system("chmod 755 /var/db/pkg-update-check/*")