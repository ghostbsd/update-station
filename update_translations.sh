#!/usr/bin/env sh

cp -f update-station update-station.py

xgettext update-station.py -o pot/update-station.pot

msgmerge -U po/zh_CN.po po/update-station.pot
msgmerge -U po/fr.po po/update-station.pot
msgmerge -U po/pt_br.po po/update-station.pot
msgmerge -U po/ru.po po/update-station.pot

rm update-station.py
