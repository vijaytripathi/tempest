# vim: tabstop=4 shiftwidth=4 softtabstop=4

# Copyright 2012 OpenStack, LLC
# All Rights Reserved.
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

import testtools

from tempest.api.compute import base
from tempest.api import utils
from tempest.common.utils.data_utils import rand_name
from tempest import exceptions
from tempest.test import attr


class ListServerFiltersTestJSON(base.BaseComputeTest):
    _interface = 'json'

    @classmethod
    def setUpClass(cls):
        super(ListServerFiltersTestJSON, cls).setUpClass()
        cls.client = cls.servers_client

        # Check to see if the alternate image ref actually exists...
        images_client = cls.images_client
        resp, images = images_client.list_images()

        if cls.image_ref != cls.image_ref_alt and \
            any([image for image in images
                 if image['id'] == cls.image_ref_alt]):
            cls.multiple_images = True
        else:
            cls.image_ref_alt = cls.image_ref

        # Do some sanity checks here. If one of the images does
        # not exist, fail early since the tests won't work...
        try:
            cls.images_client.get_image(cls.image_ref)
        except exceptions.NotFound:
            raise RuntimeError("Image %s (image_ref) was not found!" %
                               cls.image_ref)

        try:
            cls.images_client.get_image(cls.image_ref_alt)
        except exceptions.NotFound:
            raise RuntimeError("Image %s (image_ref_alt) was not found!" %
                               cls.image_ref_alt)

        cls.s1_name = rand_name('server')
        resp, cls.s1 = cls.client.create_server(cls.s1_name, cls.image_ref,
                                                cls.flavor_ref)
        cls.s2_name = rand_name('server')
        resp, cls.s2 = cls.client.create_server(cls.s2_name, cls.image_ref_alt,
                                                cls.flavor_ref)
        cls.s3_name = rand_name('server')
        resp, cls.s3 = cls.client.create_server(cls.s3_name, cls.image_ref,
                                                cls.flavor_ref_alt)

        cls.client.wait_for_server_status(cls.s1['id'], 'ACTIVE')
        resp, cls.s1 = cls.client.get_server(cls.s1['id'])
        cls.client.wait_for_server_status(cls.s2['id'], 'ACTIVE')
        resp, cls.s2 = cls.client.get_server(cls.s2['id'])
        cls.client.wait_for_server_status(cls.s3['id'], 'ACTIVE')
        resp, cls.s3 = cls.client.get_server(cls.s3['id'])

        cls.fixed_network_name = cls.config.compute.fixed_network_name

    @classmethod
    def tearDownClass(cls):
        cls.client.delete_server(cls.s1['id'])
        cls.client.delete_server(cls.s2['id'])
        cls.client.delete_server(cls.s3['id'])
        super(ListServerFiltersTestJSON, cls).tearDownClass()

    @utils.skip_unless_attr('multiple_images', 'Only one image found')
    @attr(type='gate')
    def test_list_servers_filter_by_image(self):
        # Filter the list of servers by image
        params = {'image': self.image_ref}
        resp, body = self.client.list_servers(params)
        servers = body['servers']

        self.assertIn(self.s1['id'], map(lambda x: x['id'], servers))
        self.assertNotIn(self.s2['id'], map(lambda x: x['id'], servers))
        self.assertIn(self.s3['id'], map(lambda x: x['id'], servers))

    @attr(type='gate')
    def test_list_servers_filter_by_flavor(self):
        # Filter the list of servers by flavor
        params = {'flavor': self.flavor_ref_alt}
        resp, body = self.client.list_servers(params)
        servers = body['servers']

        self.assertNotIn(self.s1['id'], map(lambda x: x['id'], servers))
        self.assertNotIn(self.s2['id'], map(lambda x: x['id'], servers))
        self.assertIn(self.s3['id'], map(lambda x: x['id'], servers))

    @attr(type='gate')
    def test_list_servers_filter_by_server_name(self):
        # Filter the list of servers by server name
        params = {'name': self.s1_name}
        resp, body = self.client.list_servers(params)
        servers = body['servers']

        self.assertIn(self.s1_name, map(lambda x: x['name'], servers))
        self.assertNotIn(self.s2_name, map(lambda x: x['name'], servers))
        self.assertNotIn(self.s3_name, map(lambda x: x['name'], servers))

    @attr(type='gate')
    def test_list_servers_filter_by_server_status(self):
        # Filter the list of servers by server status
        params = {'status': 'active'}
        resp, body = self.client.list_servers(params)
        servers = body['servers']

        self.assertIn(self.s1['id'], map(lambda x: x['id'], servers))
        self.assertIn(self.s2['id'], map(lambda x: x['id'], servers))
        self.assertIn(self.s3['id'], map(lambda x: x['id'], servers))

    @attr(type='gate')
    def test_list_servers_filter_by_limit(self):
        # Verify only the expected number of servers are returned
        params = {'limit': 1}
        resp, servers = self.client.list_servers(params)
        # when _interface='xml', one element for servers_links in servers
        self.assertEqual(1, len([x for x in servers['servers'] if 'id' in x]))

    @utils.skip_unless_attr('multiple_images', 'Only one image found')
    @attr(type='gate')
    def test_list_servers_detailed_filter_by_image(self):
        # Filter the detailed list of servers by image
        params = {'image': self.image_ref}
        resp, body = self.client.list_servers_with_detail(params)
        servers = body['servers']

        self.assertIn(self.s1['id'], map(lambda x: x['id'], servers))
        self.assertNotIn(self.s2['id'], map(lambda x: x['id'], servers))
        self.assertIn(self.s3['id'], map(lambda x: x['id'], servers))

    @attr(type='gate')
    def test_list_servers_detailed_filter_by_flavor(self):
        # Filter the detailed list of servers by flavor
        params = {'flavor': self.flavor_ref_alt}
        resp, body = self.client.list_servers_with_detail(params)
        servers = body['servers']

        self.assertNotIn(self.s1['id'], map(lambda x: x['id'], servers))
        self.assertNotIn(self.s2['id'], map(lambda x: x['id'], servers))
        self.assertIn(self.s3['id'], map(lambda x: x['id'], servers))

    @attr(type='gate')
    def test_list_servers_detailed_filter_by_server_name(self):
        # Filter the detailed list of servers by server name
        params = {'name': self.s1_name}
        resp, body = self.client.list_servers_with_detail(params)
        servers = body['servers']

        self.assertIn(self.s1_name, map(lambda x: x['name'], servers))
        self.assertNotIn(self.s2_name, map(lambda x: x['name'], servers))
        self.assertNotIn(self.s3_name, map(lambda x: x['name'], servers))

    @attr(type='gate')
    def test_list_servers_detailed_filter_by_server_status(self):
        # Filter the detailed list of servers by server status
        params = {'status': 'active'}
        resp, body = self.client.list_servers_with_detail(params)
        servers = body['servers']

        self.assertIn(self.s1['id'], map(lambda x: x['id'], servers))
        self.assertIn(self.s2['id'], map(lambda x: x['id'], servers))
        self.assertIn(self.s3['id'], map(lambda x: x['id'], servers))
        self.assertEqual(['ACTIVE'] * 3, [x['status'] for x in servers])

    @attr(type='gate')
    def test_list_servers_filtered_by_name_wildcard(self):
        # List all servers that contains 'server' in name
        params = {'name': 'server'}
        resp, body = self.client.list_servers(params)
        servers = body['servers']

        self.assertIn(self.s1_name, map(lambda x: x['name'], servers))
        self.assertIn(self.s2_name, map(lambda x: x['name'], servers))
        self.assertIn(self.s3_name, map(lambda x: x['name'], servers))

        # Let's take random part of name and try to search it
        part_name = self.s1_name[6:-1]

        params = {'name': part_name}
        resp, body = self.client.list_servers(params)
        servers = body['servers']

        self.assertIn(self.s1_name, map(lambda x: x['name'], servers))
        self.assertNotIn(self.s2_name, map(lambda x: x['name'], servers))
        self.assertNotIn(self.s3_name, map(lambda x: x['name'], servers))

    @testtools.skip('Until Bug #1170718 is resolved.')
    @attr(type='gate')
    def test_list_servers_filtered_by_ip(self):
        # Filter servers by ip
        # Here should be listed 1 server
        ip = self.s1['addresses'][self.fixed_network_name][0]['addr']
        params = {'ip': ip}
        resp, body = self.client.list_servers(params)
        servers = body['servers']

        self.assertIn(self.s1_name, map(lambda x: x['name'], servers))
        self.assertNotIn(self.s2_name, map(lambda x: x['name'], servers))
        self.assertNotIn(self.s3_name, map(lambda x: x['name'], servers))

    @attr(type='gate')
    def test_list_servers_filtered_by_ip_regex(self):
        # Filter servers by regex ip
        # List all servers filtered by part of ip address.
        # Here should be listed all servers
        ip = self.s1['addresses'][self.fixed_network_name][0]['addr'][0:-3]
        params = {'ip': ip}
        resp, body = self.client.list_servers(params)
        servers = body['servers']

        self.assertIn(self.s1_name, map(lambda x: x['name'], servers))
        self.assertIn(self.s2_name, map(lambda x: x['name'], servers))
        self.assertIn(self.s3_name, map(lambda x: x['name'], servers))

    @attr(type='gate')
    def test_list_servers_detailed_limit_results(self):
        # Verify only the expected number of detailed results are returned
        params = {'limit': 1}
        resp, servers = self.client.list_servers_with_detail(params)
        self.assertEqual(1, len(servers['servers']))


class ListServerFiltersTestXML(ListServerFiltersTestJSON):
    _interface = 'xml'
