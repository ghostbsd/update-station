#############################################################################
# Makefile for building: update-station and fbsdupdate 
#############################################################################

MAKEFILE = Makefile
DEL_FILE = rm -f
CHK_DIR_EXISTS= test -d
MKDIR = mkdir -p
COPY = cp -f
COPY_FILE = $(COPY)
COPY_DIR = $(COPY) -R
INSTALL_FILE = $(COPY_FILE)
INSTALL_PROGRAM = $(COPY_FILE)
INSTALL_DIR = $(COPY_DIR)
DEL_FILE = rm -f
SYMLINK = ln -f -s
DEL_DIR = rmdir
MOVE = mv -f
CHK_DIR_EXISTS= test -d
MKDIR = mkdir -p
PREFIX?= $(STAGEDIR)/usr/local
SUBTARGETS = \
		sub-fbsdupcheck \
		sub-upstation

sub-fbsdupcheck: fbsdupdatecheck/$(MAKEFILE) FORCE
cd fbsdupdatecheck/ && $(MAKE) -f $(MAKEFILE)
sub-fbsdupcheck-all: fbsdupdatecheck/$(MAKEFILE) FORCE
cd fbsdupdatecheck/ && $(MAKE) -f $(MAKEFILE) all
sub-fbsdupcheck-clean: fbsdupdatecheck/$(MAKEFILE) FORCE
cd fbsdupdatecheck/ && $(MAKE) -f $(MAKEFILE) clean
sub-fbsdupcheck-install_subtargets: fbsdupdatecheck/$(MAKEFILE) FORCE
cd fbsdupdatecheck/ && $(MAKE) -f $(MAKEFILE) install

sub-upstation: update-station/$(MAKEFILE) FORCE
cd update-station/ && $(MAKE) -f $(MAKEFILE)
sub-upstation-all: update-station/$(MAKEFILE) FORCE
cd update-station/ && $(MAKE) -f $(MAKEFILE) all
sub-upstation-clean: update-station/$(MAKEFILE) FORCE
cd update-station/ && $(MAKE) -f $(MAKEFILE) clean
sub-upstation-install_subtargets: update-station/$(MAKEFILE) FORCE
cd update-station/ && $(MAKE) -f $(MAKEFILE) install

####### Install

all:


install:

FORCE:
