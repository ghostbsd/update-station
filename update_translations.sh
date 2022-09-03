#!/usr/bin/env sh

cp -f update-station update-station.py

xgettext update-station.py -o src/locale/update-station.pot
msgmerge -U src/locale/ru/update-station.po src/locale/update-station.pot

rm update-station.py
