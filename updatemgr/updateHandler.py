#!/usr/local/bin/python

import os
from subprocess import Popen, PIPE, STDOUT, call


class checkUpdate():

    def __init__(self):
        p = Popen(command, shell=True, stdin=PIPE, stdout=PIPE,
    stderr=STDOUT, close_fds=True)
    probar.set_text("Installation start in progres")
    sleep(2)
    p = Popen(command, shell=True, stdin=PIPE, stdout=PIPE,
    stderr=STDOUT, close_fds=True)
    while 1:
        line = p.stdout.readline()
        #for line in p.stdout.readlines():
        if not line:
            break
        new_val = probar.get_fraction() + 0.000004
        probar.set_fraction(new_val)
        bartext = line
        probar.set_text("%s" % bartext.rstrip())
        filer = open("/home/ghostbsd/.gbi/tmp", "a")
        filer.writelines(bartext)
        filer.close
        print(bartext)
    probar.set_fraction(1.0)
    if bartext.rstrip() == "Installation finished!":
        call('python %send.py' % gbi_path, shell=True, close_fds=True)
        gobject.idle_add(window.destroy)
    else:
        call('python %serror.py' % gbi_path, shell=True, close_fds=True)
        gobject.idle_add(window.destroy)