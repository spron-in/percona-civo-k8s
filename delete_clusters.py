import requests
import os
import datetime
import dateutil.parser

delete_hours = 3
civo_key = os.environ.get('CIVO_KEY')

civo_endpoint = 'https://api.civo.com/v2/'

class civok8s:

    def __init__(self, endpoint, key):
        self.endpoint = endpoint
        self.headers = {"Authorization": "Bearer %s" % key}

    def get_request(self, endpoint_str, params = {}):

        endpoint = self.endpoint + endpoint_str
        r = requests.get(endpoint, headers=self.headers, params=params).json()
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

c = civok8s(civo_endpoint, civo_key)
def get_clusters(c):

    first_page = c.get_k8s_clusters()
    yield first_page
    pages = first_page['pages']

    for page in range(2, pages + 1):
        next_page = c.get_k8s_clusters({'page': page})
        yield next_page

for page in get_clusters(c):
    for cluster in page['items']:

        create_date = dateutil.parser.parse(cluster['created_at'])
        now = datetime.datetime.now(datetime.timezone.utc)
        diff = now - create_date

        if diff.seconds >= delete_hours*3600:
            print("[INFO] deleting old cluster with id %s" % cluster['id'])
            c.delete_k8s_cluster_by_id(cluster['id'])
