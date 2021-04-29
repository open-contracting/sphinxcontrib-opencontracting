sphinxcontrib-opencontracting |release|
=======================================

.. include:: ../README.rst

.. _field-description:

field-description
-----------------

With a ``schema.json`` file like:

.. code-block:: json

   {
     "properties": {
       "field": {
         "description": "A description"
       }
     }
   }

Use:

.. code-block:: rst

   .. field-description:: schema.json /properties/field


To render:

.. field-description:: schema.json /properties/field

.. _code-description:

code-description
-----------------

With a ``codelist.csv`` file like:

.. code-block:: none

   Code,Title,Description
   a,A,A description
   b,B,B description

Use:

.. code-block:: rst

   .. code-description:: codelist.csv a

To render:

.. code-description:: codelist.csv a

.. _extensionexplorerlinklist:

extensionexplorerlinklist
-------------------------

Add to the ``conf.py`` file:

.. code-block:: python

   extension_versions = {
       'bids': 'v1.1.5',
       'lots': 'v1.1.5',
   }

Use:

.. code-block:: rst

   .. extensionexplorerlinklist::


To render:

.. extensionexplorerlinklist::

.. _extensionlist:

extensionlist
-------------

Add to the ``conf.py`` file:

.. code-block:: python

   extension_versions = {
       'bids': 'v1.1.5',
       'lots': 'v1.1.5',
   }

Use:

.. code-block:: rst

   .. extensionlist:: The following extensions are available for the tender section
      :list: tender


To render:

.. extensionlist:: The following extensions are available for the tender section
   :list: tender

.. toctree::
   :caption: Contents

   changelog

Copyright (c) 2020 Open Contracting Partnership, released under the BSD license
