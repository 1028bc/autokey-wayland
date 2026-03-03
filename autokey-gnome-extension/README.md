autokey-gnome-extension
=======================

Forked from [window-calls](https://github.com/ickyicky/window-calls)

Added title return to some of the dbus calls for use with Autokey.

Added methods `GetMouseLocation`, `ScreenSize` and `CheckVersion`.

Refactored the Makefile to produce a ZIP file that installs properly

Added new methods to support the window script API:

- GetActiveWorkspaceIndex
- Properties
- Stick
- UnStick
- Shade
- UnShade
- MakeFullscreen
- UnMakeFullscreen
- MakeAbove
- UnMakeAbove
- Raise
- SwitchWorkspace
- ScreenSize

GJS API reference: https://gjs-docs.gnome.org/meta17~17/meta.window

How to test extensions
----------------------

https://gjs.guide/extensions/development/debugging.html

Edit extension in place: ~/.local/share/gnome-shell/extensions/autokey-gnome-extension@autokey/extension.js

Start nested GNOME shell:

    dbus-run-session gnome-shell --nested --wayland

Start terminal out of nested shell and do:

    gnome-extensions enable autokey-gnome-extension@autokey

Make calls to extension from the command line:
 
    gdbus call --session --dest org.gnome.Shell --object-path /org/gnome/Shell/Extensions/AutoKey --method org.gnome.Shell.Extensions.AutoKey.List
    gdbus call --session --dest org.gnome.Shell --object-path /org/gnome/Shell/Extensions/AutoKey --method org.gnome.Shell.Extensions.AutoKey.Properties <ID>
