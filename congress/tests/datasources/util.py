# Copyright (c) 2014 VMware, Inc. All rights reserved.
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

from __future__ import print_function
from __future__ import division
from __future__ import absolute_import


class ResponseObj(object):
    """Allows callers to use dot notation to access a dictionary."""
    def __init__(self, values):
        self.values = values

    def __getattr__(self, name):
        return self.values.get(name)

    def to_dict(self):
        return self.values
