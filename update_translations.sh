#!/usr/bin/env sh

cp -f src/update-station src/update-station.py

xgettext src/update-station.py -o src/locale/update-station.pot
msgmerge -U src/locale/ru/update-station.po src/locale/update-station.pot

rm src/update-station.py
