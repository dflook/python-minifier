Python Target Version
=====================

This package uses the version of Python that it is installed with to parse your source code.
This means that you should install python-minifier using a version of Python that is appropriate for the source code you want to minify.

The output aims to match the Python compatibility of the original source code.

There are options to configure the target versions of Python that the minified code should be compatible with, which will affect the output of the minification process.
You can specify the minimum and maximum target versions of Python that the minified code should be compatible with.

If the input source module uses syntax that is not compatible with the specified target versions, the target version range is automatically adjusted to include the syntax used in the input source module.

.. note::
   The target version options will not increase the Python compatibility of the minified code beyond the compatibility of the original source code.

   They can only be used to reduce the compatibility of the minified code to a subset of the compatibility of the original source code.

