#############################################################################
# Makefile for building: $(PREFIX)/bin/fbsdupdatecheck
#############################################################################
PREFIX?= /usr/local

####### Tools and options
PREFIX?= /usr/local
AR            = ar cqs
RANLIB        = 
TAR           = tar -cf
COMPRESS      = gzip -9f
COPY          = cp -f
SED           = sed
COPY_FILE     = $(COPY)
COPY_DIR      = $(COPY) -R
STRIP         = 
INSTALL_FILE  = $(COPY_FILE)
INSTALL_DIR   = $(COPY_DIR)
INSTALL_PROGRAM = $(COPY_FILE)
DEL_FILE      = rm -f
SYMLINK       = ln -f -s
DEL_DIR       = rmdir
MOVE          = mv -f
CHK_DIR_EXISTS= test -d
MKDIR         = mkdir -p

####### Output directory

OBJECTS_DIR   = ./

####### Files

SOURCES       = main.py
DESTDIR       = $(PREFIX)/bin/
TARGET        = fbsdupdatecheck

first: all

all: 

clean:

check: first

install_scripts: first FORCE
	@$(CHK_DIR_EXISTS) $(INSTALL_ROOT)$(DESTDIR) || $(MKDIR) $(INSTALL_ROOT)$(DESTDIR) 
	-$(INSTALL_FILE) $(SOURCES) $(INSTALL_ROOT)$(DESTDIR)$(TARGET)


uninstall_scripts:  FORCE
	-$(DEL_FILE) -r $(INSTALL_ROOT)$(PREFIX)/bin/pbreg
	-$(DEL_DIR) $(INSTALL_ROOT)$(DESTDIR)$(TARGET)


install_dochmod: first FORCE
	@$(CHK_DIR_EXISTS) $(INSTALL_ROOT)$(PREFIX)/bin/ || $(MKDIR) $(INSTALL_ROOT)$(PREFIX)/bin/ 
	chmod 755 $(DESTDIR)$(TARGET)


install:  install_scripts install_dochmod  FORCE

uninstall: uninstall_scripts   FORCE

FORCE:


