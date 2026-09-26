Update Station
==============

GhostBSD update manager. It runs as root, checks for updates in the background,
shows a tray icon when there is something to install, and installs it from a GTK
interface.

## Upgrade types

Update Station reads the GhostBSD version, which is shaped like `26.1-R15.0p13`,
and compares the running system against the repository to decide what kind of
upgrade is available.

| Upgrade | Example | How it is installed |
|---|---|---|
| Packages | newer packages, same version | In place, with an optional boot environment backup |
| Release | `26.2-R15.1p2` to `26.3-R15.1p5` | In a new boot environment |
| Minor | `26.1-R15.0p13` to `26.2-R15.1p2` | In a new boot environment, reinstalling every package |
| Major | `26.1-R14.3p8` to `26.2-R15.0` | In a new boot environment, reinstalling every package |

An upgrade installed in a boot environment never touches the running system. It
goes into a new boot environment which is activated for the next boot, so the
upgrade takes effect when you restart. Until you do, Update Station stops looking
for updates and asks for the restart instead. The boot environment it created is
yours to keep or to remove with BE Station.

A major upgrade changes the FreeBSD ABI and asks before it starts. The others do
not ask, they show the package list like any other update.

## Running

```shell
# Tray icon, checks every hour
sudo update-station

# Check right away and open the window
sudo update-station check-now
```

When the tray is already running, `check-now` signals it instead of starting a
second instance.

## Building and installing

```shell
./setup.py build
sudo ./setup.py install
```

`./setup.py clean` removes the compiled translations and `./setup.py clean_build`
removes `build`, `dist` and the egg-info directory.

## Requirements

PyGObject, requests, setuptools, bectl and distro, listed in
`requirements.txt`, plus psutil. The process name is set through libc with
`ctypes`, so no setproctitle module is needed.

## Development

```shell
# Run the tests, no GTK needed
python -m unittest discover tests

# Lint
pylint update_station/
```

## Managing Translations
To create a translation file.
```shell
./setup.py create_translation --locale=fr
```

To update translation files
```shell
./setup.py update_translations
```
