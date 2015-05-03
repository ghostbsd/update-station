#!/bin/sh

if [ -z "$1" ] ; then
   LOCALBASE=/usr/local
else
   LOCALBASE="$1"
fi

if [ -d "${LOCALBASE}/share/operator" ] ; then
   rm -rf ${LOCALBASE}/lib/update-station
fi

mkdir -p ${LOCALBASE}/lib/update-station

# Copy backend / conf / doc
cp -r updateHandler.py  ${LOCALBASE}/lib/update-station

if [ ! -d "${LOCALBASE}/etc/xdg/autostart" ] ; then
   mkdir -p ${LOCALBASE}/etc/xdg/autostart/
fi

cp -f update-station.desktop ${LOCALBASE}/etc/xdg/autostart/update-station.desktop

# Install the executable
if [ ! -d "${LOCALBASE}/bin" ] ; then
   mkdir ${LOCALBASE}/bin
fi

cp update-station.py ${LOCALBASE}/bin/update-station
chown root:operator ${LOCALBASE}/bin/update-station

chmod 755 ${LOCALBASE}/bin/update-station
