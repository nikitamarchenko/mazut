__author__ = 'nmarchenko'

from fabric.api import local, run, env
from helper.fuel import clusters, get_network, put_network

import pprint

FUEL_VM = 'fuel'

env.hosts = ['root@{}'.format(FUEL_VM)]


def init():
    local('ssh-keygen -f ~/.ssh/known_hosts -R {}'.format(FUEL_VM))
    local('ssh-keygen -f ~/.ssh/known_hosts -R 10.21.0.2')
    local('ssh-copy-id -i ~/.ssh/id_rsa.pub root@{}'.format(FUEL_VM))
    run('yum install nano htop -y')
    run('mv /etc/fuel/client/config.yaml ~/.config.yaml')
    run('echo "export FUELCLIENT_CUSTOM_SETTINGS=/root/.config.yaml" >> .bashrc')


def setup_env_network(env):
    from os import environ
    environ.setdefault("DJANGO_SETTINGS_MODULE", "devops.settings")

    from devops.models import Environment
    s = Environment.get(name=env)
    for net in s.get_networks():
        print net.name, net.ip, net.netmask, net.default_gw

    def get_net(name):
        return next(x for x in s.get_networks() if x.name == name)

    def make_ip(ip, last_octet):
        ip = str(ip.ip).split('.')
        ip[3] = str(last_octet)
        return '.'.join(ip)

    for cluster in clusters('{}:8000'.format(FUEL_VM), 'admin', 'admin'):
        net = get_network('{}:8000'.format(FUEL_VM), 'admin', 'admin', cluster['id'])

        public = get_net('public')
        management = get_net('management')
        private = get_net('private')

        net['public_vrouter_vip'] = make_ip(public, 2)
        net['public_vip'] = make_ip(public, 3)



        net['vips']['vrouter_pub']['ipaddr'] = make_ip(public, 2)  # "10.21.1.2",
        net['vips']['management']['ipaddr'] = make_ip(management, 2)  # "10.21.2.2"
        net['vips']['public']['ipaddr'] = make_ip(public, 3) # "10.21.1.3",
        net['vips']['vrouter']['ipaddr'] = make_ip(management, 2)  # "10.21.2.1",

        net['networking_parameters']['floating_ranges'] = [
          [
             make_ip(public, 130), make_ip(public, 254)
          ]
        ]

        # "internal_gateway": "10.21.3.1",
        net['networking_parameters']['internal_gateway'] = make_ip(private, 1)

        # "internal_cidr": "10.21.3.0/24",
        net['networking_parameters']['internal_cidr'] = str(get_net('private').ip)

        for network in net['networks']:

            if network['name'] == 'private':
                continue

            try:
                kvm_net = get_net(network['name'])
            except StopIteration:
                continue

            network['ip_ranges'] = [
              [
                 make_ip(kvm_net, 1), make_ip(public, 254)
              ]
            ]
            network['cidr'] = str(kvm_net.ip)

            if network['name'] == 'public':
                 network['ip_ranges'] = [
                              [
                                 make_ip(kvm_net, 2), make_ip(kvm_net, 126)
                              ] ]

            network['gateway'] = make_ip(kvm_net, 1)

        net['management_vrouter_vip'] = make_ip(management, 1)  # "10.21.2.1",
        net['management_vip'] = make_ip(management, 2)  # "10.21.2.2",

        pprint.pprint(net)
        put_network('{}:8000'.format(FUEL_VM), 'admin', 'admin', cluster['id'], net)
