repeatability
=============

To be done through using a local git repo, and writing its commit hash to the output metadata.

metadata
========

Should have the following:

* UM science settings
* UM configuration 
* Architecture/machine
* UMOV settings
* Datetime
* git hash/tag
* Logs for auditing operations

caching
=======

Caching has been done through use of a cache\_name config option. To change the cache the user must
change this option.

caching\_old
------------

Cache needs to be invalidated on the following:

* Change to settings?
* Change to code (done through git commits)
* Change to data in work (how to check this?)

Loading files
=============

Find out that loading nc files is hugely (~100x) faster as loading fields files. Write a simple
converter to turn e.g. atmos.000.pp3 into atmos.000.3.nc.
