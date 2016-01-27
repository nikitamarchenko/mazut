import requests
import json


class GetTokenKeystoneFailed(BaseException):
    pass


def get_keystone_token(endpoint, user, password):
    data = {
        "auth": {
            "tenantName": "admin",
            "passwordCredentials": {
                "username": user,
                "password": password
            }
        }
    }
    req = requests.Session()
    req.headers = {"content-type": "application/json"}
    req.verify = False
    ks = req.post('http://{}/keystone/v2.0/tokens'.format(endpoint), data=json.dumps(data))
    if ks.status_code == 200:
        token = ks.json()["access"]["token"]["id"]
        return token

    print ks.status_code

    raise GetTokenKeystoneFailed


class Session(requests.Session):

    def __init__(self):
        super(Session, self).__init__()
        self.ip = None
        self.verify = False

    def _url(self, endpoint):
        return 'http://{}/{}'.format(self.ip, endpoint)

    def get(self, endpoint, **kwargs):
        return super(Session, self).get(self._url(endpoint), **kwargs)

    def delete(self, endpoint, **kwargs):
        return super(Session, self).delete(self._url(endpoint), **kwargs)

    def put(self, endpoint, **kwargs):
        return super(Session, self).put(self._url(endpoint), **kwargs)

    def post(self, endpoint, **kwargs):
        return super(Session, self).post(self._url(endpoint), **kwargs)


def get_session(ip, login, password):
    session = Session()
    session.headers = {"X-Auth-Token": get_keystone_token(ip, login, password)}
    session.verify = False
    session.ip = ip
    return session


def clusters(ip, login, password):
    session = get_session(ip, login, password)
    clusters = session.get('api/clusters/')
    return clusters.json()


def get_network(ip, login, password, cluster_id):
    session = get_session(ip, login, password)
    neutron = session.get('api/clusters/{}/network_configuration/neutron'.format(cluster_id))
    return neutron.json()


def put_network(ip, login, password, cluster_id, config):
    session = get_session(ip, login, password)
    session.put('api/clusters/{}/network_configuration/neutron'.format(cluster_id), data=json.dumps(config))
