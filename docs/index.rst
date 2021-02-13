sphinxcontrib-opencontracting |release|
=======================================

.. include:: ../README.rst

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

codelisttable
-------------

With a ``codelist.csv`` file like:

.. code-block:: none

   Code,Title,Description
   a,A,A description
   b,B,B description

Use:

.. code-block:: rst

   .. codelisttable::
      :header-rows: 1
      :file: codelist.csv


To render:

.. codelisttable::
   :header-rows: 1
   :file: codelist.csv
