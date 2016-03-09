# Copyright 2012 Hewlett-Packard Development Company, L.P.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

from __future__ import print_function
from __future__ import division
from __future__ import absolute_import

import json
import os

import fixtures
from oslo_config import cfg

import congress.common.policy
from congress.tests import fake_policy

CONF = cfg.CONF


class PolicyFixture(fixtures.Fixture):

    def setUp(self):
        super(PolicyFixture, self).setUp()
        self.policy_dir = self.useFixture(fixtures.TempDir())
        self.policy_file_name = os.path.join(self.policy_dir.path,
                                             'policy.json')
        with open(self.policy_file_name, 'w') as policy_file:
            policy_file.write(fake_policy.policy_data)
        CONF.set_override('policy_file', self.policy_file_name, 'oslo_policy')
        congress.common.policy.reset()
        congress.common.policy.init()
        self.addCleanup(congress.common.policy.reset)


class RoleBasedPolicyFixture(fixtures.Fixture):

    def __init__(self, role="admin", *args, **kwargs):
        super(RoleBasedPolicyFixture, self).__init__(*args, **kwargs)
        self.role = role

    def setUp(self):
        """Set up the env for test.

        Copy live policy.json file and convert all actions to
        allow users of the specified role only.
        """
        super(RoleBasedPolicyFixture, self).setUp()
        policy = json.load(open(CONF.oslo_policy.policy_file))

        # Convert all actions to require specified role
        for action, rule in policy.items():
            policy[action] = 'role:%s' % self.role

        self.policy_dir = self.useFixture(fixtures.TempDir())
        self.policy_file_name = os.path.join(self.policy_dir.path,
                                             'policy.json')
        with open(self.policy_file_name, 'w') as policy_file:
            json.dump(policy, policy_file)
        CONF.set_override('policy_file', self.policy_file_name, 'oslo_policy')
        congress.common.policy.reset()
        congress.common.policy.init()
        self.addCleanup(congress.common.policy.reset)
