#!/usr/bin/env python
# how to run this:
# dotcloud info myapp.db.MASTERID | dotcloud run myapp.db.SLAVEID enslave.py
import os, re, sys
masterinfo = sys.stdin.read()
password = open('/home/dotcloud/password').read().strip()
sshhost, sshport = re.findall('ssh://dotcloud@(.*):(.*)', masterinfo)[0]
sqlhost, sqlport = re.findall('tcp://(.*):(.*)', masterinfo)[0]
sqlconn = 'host={sqlhost} port={sqlport} user=dotcloud password={password}'.format(**locals())
with open('/home/dotcloud/.ssh/config','w') as f:
    f.write('''Host master
        HostName {sshhost}
        Port {sshport}
        StrictHostKeyChecking no
        '''.format(**locals()))
os.system('''supervisorctl stop postgres''')
os.system('''psql "{sqlconn}" -c "SELECT pg_start_backup('enslave')"'''.format(**locals()))
os.system('''rsync --delete -a master:/home/dotcloud/data/ /home/dotcloud/data/''')
os.system('''psql "{sqlconn}" -c "SELECT pg_stop_backup()"'''.format(**locals()))
with open('/home/dotcloud/data/recovery.conf','w') as f:
    f.write('''
standby_mode = on
primary_conninfo = '{sqlconn}'
'''.format(**locals()))
os.system('''supervisorctl start postgres''')
