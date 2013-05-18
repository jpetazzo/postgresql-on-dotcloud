#!/usr/bin/env python
# How to run this: dotcloud run db.SLAVEID enslave MASTERID
import json, os, sys
password = open('/home/dotcloud/password').read().strip()
environ = json.load(open('/home/dotcloud/environment.json'))
masterid = sys.argv[1]
slaveid = environ['DOTCLOUD_SERVICE_ID']
servicename = environ['DOTCLOUD_SERVICE_NAME'].upper()
sshhost = environ['DOTCLOUD_{0}_SSH_HOST_{1}'.format(servicename, masterid)]
sshport = environ['DOTCLOUD_{0}_SSH_PORT_{1}'.format(servicename, masterid)]
sqlhost = environ['DOTCLOUD_{0}_PGSQL_HOST_{1}'.format(servicename, masterid)]
sqlport = environ['DOTCLOUD_{0}_PGSQL_PORT_{1}'.format(servicename, masterid)]
sqlconn = ('host={sqlhost} port={sqlport} user=dotcloud password={password} '
           'dbname=template1'.format(**locals()))
with open('/home/dotcloud/.ssh/config','w') as f:
    f.write('''Host master
        HostName {sshhost}
        Port {sshport}
        StrictHostKeyChecking no
        '''.format(**locals()))
os.system('''supervisorctl stop postgres''')
os.system('''psql "{sqlconn}" -c "SELECT pg_start_backup('enslave{slaveid}')"'''
          .format(**locals()))
os.system('''rsync --delete -a master:/home/dotcloud/data/ /home/dotcloud/data/''')
os.system('''psql "{sqlconn}" -c "SELECT pg_stop_backup()"'''.format(**locals()))
with open('/home/dotcloud/data/recovery.conf','w') as f:
    f.write('''
standby_mode = on
primary_conninfo = '{sqlconn}'
'''.format(**locals()))
os.system('''supervisorctl start postgres''')
