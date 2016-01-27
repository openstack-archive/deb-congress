# Copyright (c) 2015 OpenStack Foundation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from oslo_config import cfg

from congress.api import table_model
from congress import harness
from congress.managers import datasource as datasource_manager
from congress.tests import base
from congress.tests import helper


class TestTableModel(base.SqlTestCase):
    def setUp(self):
        super(TestTableModel, self).setUp()
        # Here we load the fake driver
        cfg.CONF.set_override(
            'drivers',
            ['congress.tests.fake_datasource.FakeDataSource'])

        # NOTE(masa): this set of tests, tests to deeply. We don't have
        # any tests currently testing cage. Once we do we should mock out
        # cage so we don't have to create one here.

        self.cage = harness.create(helper.root_path())
        self.ds_mgr = datasource_manager.DataSourceManager
        self.ds_mgr.validate_configured_drivers()
        req = {'driver': 'fake_datasource',
               'name': 'fake_datasource'}
        req['config'] = {'auth_url': 'foo',
                         'username': 'foo',
                         'password': 'password',
                         'tenant_name': 'foo'}
        self.datasource = self.ds_mgr.add_datasource(req)
        self.engine = self.cage.service_object('engine')
        self.api_rule = self.cage.service_object('api-rule')
        self.table_model = table_model.TableModel("table_model", {},
                                                  policy_engine=self.engine,
                                                  datasource_mgr=self.ds_mgr)

    def tearDown(self):
        super(TestTableModel, self).tearDown()

    def test_get_datasource_table_with_id(self):
        context = {'ds_id': self.datasource['id'],
                   'table_id': 'fake_table'}
        expected_ret = {'id': 'fake_table'}
        ret = self.table_model.get_item('fake_table', {}, context)
        self.assertEqual(expected_ret, ret)

    def test_get_datasource_table_with_name(self):
        context = {'ds_id': self.datasource['name'],
                   'table_id': 'fake_table'}
        expected_ret = {'id': 'fake_table'}
        ret = self.table_model.get_item('fake_table', {}, context)
        self.assertEqual(expected_ret, ret)

    def test_get_invalid_datasource(self):
        context = {'ds_id': 'invalid-id',
                   'table_id': 'fake_table'}
        expected_ret = None

        ret = self.table_model.get_item('fake_table', {}, context)
        self.assertEqual(expected_ret, ret)

    def test_get_invalid_datasource_table(self):
        context = {'ds_id': self.datasource['id'],
                   'table_id': 'invalid-table'}
        expected_ret = None
        ret = self.table_model.get_item('invalid-table', {}, context)
        self.assertEqual(expected_ret, ret)

    def test_get_policy_table(self):
        context = {'policy_id': self.engine.DEFAULT_THEORY,
                   'table_id': 'p'}
        expected_ret = {'id': 'p'}

        self.api_rule.add_item({'rule': 'p(x) :- q(x)'}, {}, context=context)
        self.api_rule.add_item({'rule': 'q(x) :- r(x)'}, {}, context=context)

        ret = self.table_model.get_item('p', {}, context)
        self.assertEqual(expected_ret, ret)

    def test_get_invalid_policy(self):
        context = {'policy_id': self.engine.DEFAULT_THEORY,
                   'table_id': 'fake-table'}
        invalid_context = {'policy_id': 'invalid-policy',
                           'table_id': 'fake-table'}
        expected_ret = None

        self.api_rule.add_item({'rule': 'p(x) :- q(x)'}, {}, context=context)
        self.api_rule.add_item({'rule': 'q(x) :- r(x)'}, {}, context=context)

        ret = self.table_model.get_item(self.engine.DEFAULT_THEORY,
                                        {}, invalid_context)
        self.assertEqual(expected_ret, ret)

    def test_get_invalid_policy_table(self):
        context = {'policy_id': self.engine.DEFAULT_THEORY,
                   'table_id': 'fake-table'}
        invalid_context = {'policy_id': self.engine.DEFAULT_THEORY,
                           'table_id': 'invalid-name'}
        expected_ret = None

        self.api_rule.add_item({'rule': 'p(x) :- q(x)'}, {}, context=context)
        self.api_rule.add_item({'rule': 'q(x) :- r(x)'}, {}, context=context)

        ret = self.table_model.get_item(self.engine.DEFAULT_THEORY, {},
                                        invalid_context)
        self.assertEqual(expected_ret, ret)

    def test_get_items_datasource_table(self):
        context = {'ds_id': self.datasource['id']}
        expected_ret = {'results': [{'id': 'fake_table'}]}

        ret = self.table_model.get_items({}, context)
        self.assertEqual(expected_ret, ret)

    def test_get_items_invalid_datasource(self):
        context = {'ds_id': 'invalid-id',
                   'table_id': 'fake-table'}

        ret = self.table_model.get_items({}, context)
        self.assertIsNone(ret)

    def _get_id_list_from_return(self, result):
        return [r['id'] for r in result['results']]

    def test_get_items_policy_table(self):
        context = {'policy_id': self.engine.DEFAULT_THEORY}
        expected_ret = {'results': [{'id': x} for x in ['q', 'p', 'r']]}

        self.api_rule.add_item({'rule': 'p(x) :- q(x)'}, {}, context=context)
        self.api_rule.add_item({'rule': 'q(x) :- r(x)'}, {}, context=context)

        ret = self.table_model.get_items({}, context)
        self.assertEqual(set(self._get_id_list_from_return(expected_ret)),
                         set(self._get_id_list_from_return(ret)))

    def test_get_items_invalid_policy(self):
        context = {'policy_id': self.engine.DEFAULT_THEORY}
        invalid_context = {'policy_id': 'invalid-policy'}
        expected_ret = None

        self.api_rule.add_item({'rule': 'p(x) :- q(x)'}, {}, context=context)
        self.api_rule.add_item({'rule': 'q(x) :- r(x)'}, {}, context=context)

        ret = self.table_model.get_items({}, invalid_context)
        self.assertEqual(expected_ret, ret)
