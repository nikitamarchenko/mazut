__author__ = 'nmarchenko'

from fabric.api import local, run, env

FUEL_VM = 'fuel'

env.hosts = ['root@{}'.format(FUEL_VM)]


def init():
    local('ssh-keygen -f "/home/nmarchenko/.ssh/known_hosts" -R {}'.format(FUEL_VM))
    local('ssh-keygen -f "/home/nmarchenko/.ssh/known_hosts" -R 10.20.0.2')
    local('ssh-copy-id -i ~/.ssh/id_rsa.pub root@{}'.format(FUEL_VM))
    run('yum install nano htop -y')
    run('mv /etc/fuel/client/config.yaml ~/.config.yaml')
    run('echo "export FUELCLIENT_CUSTOM_SETTINGS=/root/.config.yaml" >> .bashrc')
