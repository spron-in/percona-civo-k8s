import requests
import random
import string
import flask
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import os

civo_key = os.environ.get('CIVO_KEY')
try:
    civo_instance = os.environ.get('CIVO_INSTANCE')
except:
    civo_instance = "g4s.kube.large"

try:
    civo_network_id = os.environ.get('CIVO_NETWORK_ID')
except:
    print("Network ID is mandatory")

civo_endpoint = 'https://api.civo.com/v2/'
headers = {"Authorization": "Bearer %s" % civo_key}


class civok8s:

    def __init__(self, endpoint, key):
        self.endpoint = endpoint
        self.headers = {"Authorization": "Bearer %s" % key}

    def get_request(self, endpoint_str):

        endpoint = self.endpoint + endpoint_str
        r = requests.get(endpoint, headers=self.headers).json()
        return r

    def post_request(self, endpoint_str, data):

        endpoint = self.endpoint + endpoint_str
        r = requests.post(endpoint, data=data, headers=self.headers).json()
        return r

    def delete_request(self, endpoint_str):

        endpoint = self.endpoint + endpoint_str
        r = requests.delete(endpoint, headers=self.headers).json()
        return r

    def get_k8s_clusters(self):

        return self.get_request('kubernetes/clusters')

    def create_k8s_cluster(self, data):

        k8s_cluster = self.post_request('kubernetes/clusters', data)
        return k8s_cluster['id']

    def get_k8s_cluster_config(self, k8s_id):

        k8s_cluster = self.get_request('kubernetes/clusters/%s' % k8s_id)
        return k8s_cluster['kubeconfig']

    def get_k8s_cluster_by_id(self, k8s_id):

        return self.get_request('kubernetes/clusters/%s' % k8s_id)

    def delete_k8s_cluster_by_id(self, k8s_id):

        return self.delete_request('kubernetes/clusters/%s' % k8s_id)


app = flask.Flask(__name__)

limiter = Limiter(
    app,
    key_func=get_remote_address,
    default_limits=["600 per day", "120 per hour"]
)

@app.route('/create_k8s', methods=['GET'])
@limiter.limit("1 per day")
def create_k8s():
    c = civok8s(civo_endpoint, civo_key)

    k8s_config = {
        'name': ''.join(random.choice(string.ascii_lowercase) for i in range(12)),
        'num_target_nodes': 3,
        'target_nodes_size': civo_instance,
        'network_id': civo_network_id
    }
    try:
        cluster_id = c.create_k8s_cluster(k8s_config)
    except:
        return "Something went wrong"

    return cluster_id

@app.route('/get_k8s_config/<string:k8s_id>' , methods=['GET'])
def get_k8s_config(k8s_id):
    c = civok8s(civo_endpoint, civo_key)

    try:
        kube_config = c.get_k8s_cluster_config(k8s_id)
    except:
        return "Something went wrong"

    if kube_config == None:
        kube_config = "Cluster is not ready yet"

    return kube_config

@app.route('/delete_k8s/<string:k8s_id>' , methods=['GET'])
def delete_k8s(k8s_id):
    c = civok8s(civo_endpoint, civo_key)

    return c.delete_k8s_cluster_by_id(k8s_id)

app.run(host='0.0.0.0')
