PostgreSQL master/slave for dotCloud
====================================

.. warning::

   This recipe is alpha quality.


Basic Setup
-----------

::

   git clone git://github.com/jpetazzo/postgresql-on-dotcloud.git
   dotcloud create myapp
   dotcloud push

The superuser will be ``dotcloud`` (not ``root`` nor ``postgres``).
The password will be shown at the end of the build process. You can
also retrieve it by running::

   dotcloud run db cat password


Change PostgreSQL Version
-------------------------

The version of PostgreSQL is specified in the ``dotcloud.yml`` file.
You can change it at any time, and repush. The requested version will
be downloaded and compiled. Previous builds are kept, so rolling back
to an old version (which was already installed before) won't require
a full rebuild.


Master/Slave Setup
------------------

By default, this recipe deploys a single PostgreSQL master.
To provision a slave, you need to do this::

   dotcloud scale db=2
   dotcloud info db.0 | dotcloud run db.1 /home/dotcloud/enslave.py

This last line will make myapp.db.1 a slave of myapp.db.0.
The ``enslave.py`` script will read the ``dotcloud info`` blurb on ``stdin``,
extract the SSH and SQL port information, stop the slave ``postgres`` process,
start a backup process on the master, transfer the ``PGDATA`` directory from
the master to the slave, complete the backup process, create the replication
parameters (the ``recovery.conf`` file), and restart the slave ``postgres``
process.


Failover
--------

The failover is not automatic. You must do this::

   dotcloud run db.1 rm /home/dotcloud/data/recovery.conf
   dotcloud run db.1 supervisorctl restart postgres

And then update your app configuration to point to the promoted slave
instead of the master. You can rerun the "enslave" procedure described
above at anytime, but remember that the master data will overwrite the
slave data. Remember to use the correct instance numbers!


Multi-Slave Setup
-----------------

It should work with multiple slaves without a problem. Just provision each
slave individually.

.. note::

   Don't try to cascade slaves unless you know what you're doing.
   If you setup N slaves, if you promote 1 slave to be master, the
   other slaves should be reconfigured to talk to the new master.
   Yes, this could mean a lengthy reprovisioning process.


