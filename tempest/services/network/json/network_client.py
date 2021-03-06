# vim: tabstop=4 shiftwidth=4 softtabstop=4
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import json

from tempest.common.rest_client import RestClient


class NetworkClient(RestClient):

    """
    Tempest REST client for Neutron. Uses v2 of the Neutron API, since the
    V1 API has been removed from the code base.

    Implements create, delete, list and show for the basic Neutron
    abstractions (networks, sub-networks and ports):

    It also implements list, show, update and reset for OpenStack Networking
    quotas
    """

    def __init__(self, config, username, password, auth_url, tenant_name=None):
        super(NetworkClient, self).__init__(config, username, password,
                                            auth_url, tenant_name)
        self.service = self.config.network.catalog_type
        self.version = '2.0'
        self.uri_prefix = "v%s" % (self.version)

    def list_networks(self):
        uri = '%s/networks' % (self.uri_prefix)
        resp, body = self.get(uri, self.headers)
        body = json.loads(body)
        return resp, body

    def create_network(self, name):
        post_body = {
            'network': {
                'name': name,
            }
        }
        body = json.dumps(post_body)
        uri = '%s/networks' % (self.uri_prefix)
        resp, body = self.post(uri, headers=self.headers, body=body)
        body = json.loads(body)
        return resp, body

    def show_network(self, uuid):
        uri = '%s/networks/%s' % (self.uri_prefix, uuid)
        resp, body = self.get(uri, self.headers)
        body = json.loads(body)
        return resp, body

    def delete_network(self, uuid):
        uri = '%s/networks/%s' % (self.uri_prefix, uuid)
        resp, body = self.delete(uri, self.headers)
        return resp, body

    def create_subnet(self, net_uuid, cidr):
        post_body = dict(
            subnet=dict(
                ip_version=4,
                network_id=net_uuid,
                cidr=cidr),)
        body = json.dumps(post_body)
        uri = '%s/subnets' % (self.uri_prefix)
        resp, body = self.post(uri, headers=self.headers, body=body)
        body = json.loads(body)
        return resp, body

    def delete_subnet(self, uuid):
        uri = '%s/subnets/%s' % (self.uri_prefix, uuid)
        resp, body = self.delete(uri, self.headers)
        return resp, body

    def list_subnets(self):
        uri = '%s/subnets' % (self.uri_prefix)
        resp, body = self.get(uri, self.headers)
        body = json.loads(body)
        return resp, body

    def show_subnet(self, uuid):
        uri = '%s/subnets/%s' % (self.uri_prefix, uuid)
        resp, body = self.get(uri, self.headers)
        body = json.loads(body)
        return resp, body

    def create_port(self, network_id, state=None):
        if not state:
            state = True
        post_body = {
            'port': {
                'network_id': network_id,
                'admin_state_up': state,
            }
        }
        body = json.dumps(post_body)
        uri = '%s/ports' % (self.uri_prefix)
        resp, body = self.post(uri, headers=self.headers, body=body)
        body = json.loads(body)
        return resp, body

    def delete_port(self, port_id):
        uri = '%s/ports/%s' % (self.uri_prefix, port_id)
        resp, body = self.delete(uri, self.headers)
        return resp, body

    def list_ports(self):
        uri = '%s/ports' % (self.uri_prefix)
        resp, body = self.get(uri, self.headers)
        body = json.loads(body)
        return resp, body

    def show_port(self, port_id):
        uri = '%s/ports/%s' % (self.uri_prefix, port_id)
        resp, body = self.get(uri, self.headers)
        body = json.loads(body)
        return resp, body

    def update_quotas(self, tenant_id, **kwargs):
        put_body = {'quota': kwargs}
        body = json.dumps(put_body)
        uri = '%s/quotas/%s' % (self.uri_prefix, tenant_id)
        resp, body = self.put(uri, body, self.headers)
        body = json.loads(body)
        return resp, body['quota']

    def show_quotas(self, tenant_id):
        uri = '%s/quotas/%s' % (self.uri_prefix, tenant_id)
        resp, body = self.get(uri, self.headers)
        body = json.loads(body)
        return resp, body['quota']

    def reset_quotas(self, tenant_id):
        uri = '%s/quotas/%s' % (self.uri_prefix, tenant_id)
        resp, body = self.delete(uri, self.headers)
        return resp, body

    def list_quotas(self):
        uri = '%s/quotas' % (self.uri_prefix)
        resp, body = self.get(uri, self.headers)
        body = json.loads(body)
        return resp, body['quotas']

    def update_subnet(self, subnet_id, new_name):
        put_body = {
            'subnet': {
                'name': new_name,
            }
        }
        body = json.dumps(put_body)
        uri = '%s/subnets/%s' % (self.uri_prefix, subnet_id)
        resp, body = self.put(uri, body=body, headers=self.headers)
        body = json.loads(body)
        return resp, body

    def update_port(self, port_id, new_name):
        put_body = {
            'port': {
                'name': new_name,
            }
        }
        body = json.dumps(put_body)
        uri = '%s/ports/%s' % (self.uri_prefix, port_id)
        resp, body = self.put(uri, body=body, headers=self.headers)
        body = json.loads(body)
        return resp, body

    def update_network(self, network_id, new_name):
        put_body = {
            "network": {
                "name": new_name,
            }
        }
        body = json.dumps(put_body)
        uri = '%s/networks/%s' % (self.uri_prefix, network_id)
        resp, body = self.put(uri, body=body, headers=self.headers)
        body = json.loads(body)
        return resp, body
