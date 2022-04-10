Minification Options
====================

These transforms can be optionally enabled when minifying. Some are enabled by default as they are always or almost
always safe.

They can be enabled or disabled through the minify function, or passing options to the pyminify command.

.. toctree::
   :caption: Enabled by default
   :maxdepth: 1

   combine_imports
   remove_pass
   hoist_literals
   remove_annotations
   rename_locals
   remove_object_base
   convert_posargs_to_args
   preserve_shebang

.. toctree::
   :caption: Disabled by default
   :maxdepth: 1

   remove_literal_statements
   rename_globals
