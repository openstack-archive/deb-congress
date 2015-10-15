# Copyright (c) 2015 Intel, Inc. All rights reserved.
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
#

from congress.api import webservice
from congress.dse import deepsix
from congress import exception


def d6service(name, keys, inbox, datapath, args):
    return ActionsModel(name, keys, inbox=inbox, dataPath=datapath, **args)


class ActionsModel(deepsix.deepSix):
    """Model for handling API requests about Actions."""
    def __init__(self, name, keys, inbox=None, dataPath=None,
                 policy_engine=None):
        super(ActionsModel, self).__init__(name, keys, inbox=inbox,
                                           dataPath=dataPath)
        assert policy_engine is not None
        self.engine = policy_engine

    def get_items(self, params, context=None):
        """Retrieve items from this model.

        Args:
            params: A dict-like object containing parameters
                    from the request query string and body.
            context: Key-values providing frame of reference of request

        Returns:
             A dict containing at least a 'actions' key whose value is a list
             of items in this model.
        """
        if 'ds_id' in context:
            id_ = context['ds_id']
            service = self.engine.d6cage.getservice(id_,
                                                    type_='datasource_driver')
            if service:
                return service['object'].get_actions()

            raise webservice.DataModelException(
                exception.NotFound.code,
                'Could not find service %s' % id_,
                http_status_code=exception.NotFound.code)
        raise Exception("Could not find expected parameters for action call. "
                        "Context: %s" % str(context))
