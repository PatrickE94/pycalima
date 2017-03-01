========
PyCalima
========
Simple python interface against the
`Pax Calima® <http://www.pax.se/sv/produkt/calima/pax-calima-flakt>`_
bathroom fan created and sold by `Pax® <http://www.pax.se>`_

This module provides a very simple interface against the various
GATT characteristics of the Calima fan, most importantly it handles the
authentication so values are actually persisted within the fan.

Uses `BluePy <https://github.com/IanHarvey/bluepy>`_

Demo usage
----------
.. code:: python

  from Calima import Calima

  fan = Calima("MA:CC:AD:DR:ES:SS", "012345")
  print(fan.getAlias())

Command line tool
-----------------
The module includes a very simple commandline tool which prints all
the characteristics of a fan and then the State every two seonds. It can
also search for available fans if you don't the MAC address.

For more on using the tool, just run `calima -h`.

Documentation
-------------
There is currently no documentation yet, check the Calima.py file to
see available functions.

License
-------
See LICENSE file
