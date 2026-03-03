window API
==========

These API methods are available when running in all environments.

This class is invoked as the "window" class in AutoKey scripts.  For example, the
"autokey.scripting.window_gnome.Window.activate()" method documented below is
called as "window.activate()" in an AutoKey script.

There are two different implementations of the "window" class, one for GNOME/Wayland environments one for X11.  They both offer the exact same methods, so only the GNOME/Wayland version is shown in this documentation.

.. automodule:: autokey.common
   :no-members:

.. automodule:: autokey.gtkapp
   :no-members:

.. automodule:: autokey.scripting.window_gnome
   :no-members:

.. autoclass:: Window
   :members:
