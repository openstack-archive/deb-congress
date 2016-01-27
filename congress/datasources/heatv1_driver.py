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

import heatclient.v1.client as heatclient
import keystoneclient.v2_0.client as ksclient
from oslo_log import log as logging

from congress.datasources import datasource_driver
from congress.datasources import datasource_utils as ds_utils

LOG = logging.getLogger(__name__)


def d6service(name, keys, inbox, datapath, args):
    """This method is called by d6cage to create a dataservice instance."""
    return HeatV1Driver(name, keys, inbox, datapath, args)


class HeatV1Driver(datasource_driver.PollingDataSourceDriver,
                   datasource_driver.ExecutionDriver):

    STACKS = "stacks"
    STACKS_LINKS = "stacks_links"
    DEPLOYMENTS = "deployments"
    DEPLOYMENT_OUTPUT_VALUES = "deployment_output_values"

    # TODO(thinrichs): add resources, events, snapshots
    value_trans = {'translation-type': 'VALUE'}
    stacks_links_translator = {
        'translation-type': 'HDICT',
        'table-name': STACKS_LINKS,
        'parent-key': 'id',
        'selector-type': 'DICT_SELECTOR',
        'in-list': True,
        'field-translators':
            ({'fieldname': 'href', 'translator': value_trans},
             {'fieldname': 'rel', 'translator': value_trans})}

    stacks_translator = {
        'translation-type': 'HDICT',
        'table-name': STACKS,
        'selector-type': 'DOT_SELECTOR',
        'field-translators':
        ({'fieldname': 'id', 'translator': value_trans},
         {'fieldname': 'stack_name', 'translator': value_trans},
         {'fieldname': 'description', 'translator': value_trans},
         {'fieldname': 'creation_time', 'translator': value_trans},
         {'fieldname': 'updated_time', 'translator': value_trans},
         {'fieldname': 'stack_status', 'translator': value_trans},
         {'fieldname': 'stack_status_reason', 'translator': value_trans},
         {'fieldname': 'stack_owner', 'translator': value_trans},
         {'fieldname': 'parent', 'translator': value_trans},
         {'fieldname': 'links', 'translator': stacks_links_translator})}

    deployments_output_values_translator = {
        'translation-type': 'HDICT',
        'table-name': DEPLOYMENT_OUTPUT_VALUES,
        'parent-key': 'id',
        'selector-type': 'DICT_SELECTOR',
        'field-translators':
            ({'fieldname': 'deploy_stdout', 'translator': value_trans},
             {'fieldname': 'deploy_stderr', 'translator': value_trans},
             {'fieldname': 'deploy_status_code', 'translator': value_trans},
             {'fieldname': 'result', 'translator': value_trans})}

    software_deployment_translator = {
        'translation-type': 'HDICT',
        'table-name': DEPLOYMENTS,
        'selector-type': 'DOT_SELECTOR',
        'field-translators':
        ({'fieldname': 'status', 'translator': value_trans},
         {'fieldname': 'server_id', 'translator': value_trans},
         {'fieldname': 'config_id', 'translator': value_trans},
         {'fieldname': 'action', 'translator': value_trans},
         {'fieldname': 'status_reason', 'translator': value_trans},
         {'fieldname': 'id', 'translator': value_trans},
         {'fieldname': 'output_values',
          'translator': deployments_output_values_translator})}

    TRANSLATORS = [stacks_translator, software_deployment_translator]

    def __init__(self, name='', keys='', inbox=None, datapath=None, args=None):
        super(HeatV1Driver, self).__init__(name, keys, inbox, datapath, args)
        datasource_driver.ExecutionDriver.__init__(self)
        self.creds = args

        keystone = ksclient.Client(**self.creds)
        endpoint = keystone.service_catalog.url_for(
            service_type='orchestration', endpoint_type='publicURL')
        self.heat = heatclient.Client(endpoint, token=keystone.auth_token)
        self._init_end_start_poll()

    @staticmethod
    def get_datasource_info():
        result = {}
        result['id'] = 'heat'
        result['description'] = ('Datasource driver that interfaces with'
                                 ' Openstack orchestration aka heat.')
        result['config'] = ds_utils.get_openstack_required_config()
        result['secret'] = ['password']
        return result

    def update_from_datasource(self):
        """Called when it is time to pull new data from this datasource."""
        LOG.debug("Grabbing Heat Stacks")
        stacks = {'stacks': self.heat.stacks.list()}
        self._translate_stacks(stacks)

        LOG.debug("Grabbing the software deployments")
        deployments = {'deployments': self.heat.software_deployments.list()}
        self._translate_software_deployment(deployments)

    @ds_utils.update_state_on_changed(STACKS)
    def _translate_stacks(self, obj):
        """Translate the stacks represented by OBJ into tables."""
        LOG.debug("STACKS: %s", str(dict(obj)))
        row_data = HeatV1Driver.convert_objs(
            obj['stacks'], HeatV1Driver.stacks_translator)
        return row_data

    @ds_utils.update_state_on_changed(DEPLOYMENTS)
    def _translate_software_deployment(self, obj):
        """Translate the stacks represented by OBJ into tables."""
        LOG.debug("Software Deployments: %s", str(dict(obj)))
        row_data = HeatV1Driver.convert_objs(
            obj['deployments'], HeatV1Driver.software_deployment_translator)
        return row_data

    def execute(self, action, action_args):
        """Overwrite ExecutionDriver.execute()."""
        # action can be written as a method or an API call.
        func = getattr(self, action, None)
        if func and self.is_executable(func):
            func(action_args)
        else:
            self._execute_api(self.heat, action, action_args)
