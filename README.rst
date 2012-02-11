PostgreSQL master/slave for dotCloud
====================================

.. warning::

   This recipe is alpha quality.

::

    git clone
    dotcloud push myapp postgresql-on-dotcloud.git
    dotcloud info myapp.db.0 | dotcloud run myapp.db.1 /home/dotcloud/enslave.py

This last line will make myapp.db.1 a slave of myapp.db.0.
The ``enslave.py`` script will read the ``dotcloud info`` blurb on ``stdin``,
extract the SSH and SQL port information, stop the slave ``postgres`` process,
start a backup process on the master, transfer the ``PGDATA`` directory from
the master to the slave, complete the backup process, create the replication
parameters (the ``recovery.conf`` file), and restart the slave ``postgres``
process.

It should work with multiple slaves without a problem.

.. note::

   Don't try to cascade slaves unless you know what you're doing.
   If you setup N slaves, if you promote 1 slave to be master, the
   other slaves should be reconfigured to talk to the new master.
   Yes, this could mean a lengthy reprovisioning process.

