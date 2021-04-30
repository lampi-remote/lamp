#! /usr/bin/env python

# some hackery with gevent...
from gevent import monkey
monkey.patch_all()

import paramiko  # noqa
from pssh.pssh_client import ParallelSSHClient  # noqa
from gevent import joinall  # noqa

target_public = 'mqtt://ec2-54-82-195-133.compute-1.amazonaws.com:50001'

master_public = 'ec2-52-90-56-18.compute-1.amazonaws.com'
master_private = 'ip-172-31-9-166.ec2.internal'

slaves = [
    'ec2-34-201-44-62.compute-1.amazonaws.com',
    'ec2-34-207-78-220.compute-1.amazonaws.com',
    'ec2-34-239-247-190.compute-1.amazonaws.com',
    'ec2-52-23-174-73.compute-1.amazonaws.com',
    'ec2-54-89-172-30.compute-1.amazonaws.com',
    'ec2-54-157-13-35.compute-1.amazonaws.com',
    'ec2-54-209-21-173.compute-1.amazonaws.com',
    'ec2-54-209-144-193.compute-1.amazonaws.com',
    'ec2-54-227-191-220.compute-1.amazonaws.com',
    'ec2-54-237-238-149.compute-1.amazonaws.com',
]

key_file_path = '/Users/nbarendt/.ssh/eecs397-spring17.pem'
priv_key = paramiko.RSAKey.from_private_key_file(key_file_path)

master_client = ParallelSSHClient([master_public], pkey=priv_key)
slave_client = ParallelSSHClient(slaves, pkey=priv_key)

# kill any locust processes
print("killing any 'locust' processes in cluster...")
master_output = master_client.run_command('killall -q locust', sudo=True)
slave_output = slave_client.run_command('killall -q locust', sudo=True)

master_client.join(master_output)
slave_client.join(slave_output)

print("   done")

# SFTP latest locust file to all locust instances
print("copying latest mqtt-locustfile.py to all cluster instances")
master_greenlets = master_client.copy_file('mqtt-locustfile.py',
                                           'mqtt-locust/eecs397-locustfile.py')
slave_greenlets = slave_client.copy_file('mqtt-locustfile.py',
                                         'mqtt-locust/eecs397-locustfile.py')

joinall(master_greenlets, raise_error=True)
joinall(slave_greenlets, raise_error=True)

print("   done")

# Start locust
print("starting locust on master and slave instances")

# master_cmd = ("cd ~/mqtt-locust;"
#               " locust --master --host={}").format(target_public)
# master_output = master_client.run_command(master_cmd, sudo=True)
slave_cmd = ("cd ~/mqtt-locust; locust --slave --master-host={}"
             " -f eecs397-locustfile.py --host={}").format(master_private,
                                                           target_public)
slave_output = slave_client.run_command(slave_cmd, sudo=True)

print("point your browser to http://{}:8089".format(master_public))
print("(Use CTRL-C to Quit")

# master_client.join(master_output)
slave_client.join(slave_output)
