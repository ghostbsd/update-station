#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys
from setuptools import setup, Command, glob

from DistUtilsExtra.command.build_extra import build_extra
from DistUtilsExtra.command.build_i18n import build_i18n
from DistUtilsExtra.command.clean_i18n import clean_i18n

# to update i18n .mo files (and merge .pot file into .po files) run on Linux:
# python setup.py build_i18n -m''

__VERSION__ = '5.9'

PROGRAM_VERSION = __VERSION__
prefix = sys.prefix


def data_file_list(install_base, source_base):
    data = []
    for root, subFolders, files in os.walk(source_base):
        file_list = []
        for f in files:
            file_list.append(os.path.join(root, f))
        data.append((root.replace(source_base, install_base), file_list))
    return data


class UpdateTranslationsCommand(Command):
    """Custom command to extract messages and update .po files."""

    description = 'Extract messages to .pot and update .po'
    user_options = []  # No custom options

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        # Define paths
        pot_file = 'po/update-station.pot'
        po_files = glob.glob('po/*.po')
        # Step 1: Extract messages to .pot file
        print("Extracting messages to .pot file...")
        os.system(f'xgettext --from-code=UTF-8 -L Python -o {pot_file} update_station/*.py update-station')
        # Step 2: Update .po files with the new .pot file
        print("Updating .po files with new translations...")
        for po_file in po_files:
            print(f"Updating {po_file}...")
            os.system(f'msgmerge -U {po_file} {pot_file}')
        print("Translation update complete.")


class CreateTranslationCommand(Command):
    """Custom command to create a new .po file for a specific language."""
    locale = None
    description = 'Create a new .po file for the specified language'
    user_options = [
        ('locale=', 'l', 'Locale code for the new translation (e.g., fr, es)')
    ]

    def initialize_options(self):
        self.locale = None  # Initialize the locale option to None

    def finalize_options(self):
        if self.locale is None:
            raise Exception("You must specify the locale code (e.g., --locale=fr)")

    def run(self):
        # Define paths
        pot_file = 'po/update-station.pot'
        po_dir = 'po'
        po_file = os.path.join(po_dir, f'{self.locale}.po')
        # Check if the .pot file exists
        if not os.path.exists(pot_file):
            print("Extracting messages to .pot file...")
            os.system(f'xgettext --from-code=UTF-8 -L Python -o {pot_file} update_station/*.py update-station')
        # Create the new .po file
        if not os.path.exists(po_file):
            print(f"Creating new {po_file} for locale '{self.locale}'...")
            os.makedirs(po_dir, exist_ok=True)
            os.system(f'msginit --locale={self.locale} --input={pot_file} --output-file={po_file}')
        else:
            print(f"PO file for locale '{self.locale}' already exists: {po_file}")


data_files = [
    (f'{prefix}/etc/xdg/autostart', ['src/update-station.desktop']),
    (f'{prefix}/share/applications', ['src/update-manager.desktop']),
    (f'{prefix}/lib/update-station', ['src/need_reboot.json', 'src/pkg_to_reinstall']),
    (f'{prefix}/etc/sudoers.d', ['src/sudoers.d/update-station'])
]

data_files.extend(data_file_list(f'{prefix}/share/locale', 'build/mo'))

setup(
    name="update-station",
    version=PROGRAM_VERSION,
    description="Update Manager For GhostBSD/FreeBSD",
    license='BSD',
    author='Eric Turgeon',
    url='https://github/GhostBSD/update-station/',
    package_dir={'': '.'},
    data_files=data_files,
    install_requires=['setuptools'],
    packages=['update_station'],
    scripts=['update-station'],
    cmdclass={
        'create_translation': CreateTranslationCommand,
        'update_translations': UpdateTranslationsCommand,
        "build": build_extra,
        "build_i18n": build_i18n,
        "clean": clean_i18n
    }
)
