# Copyright 2015 Intel Corp
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

from oslo_config import cfg

from tempest import config  # noqa


service_available_group = cfg.OptGroup(name="service_available",
                                       title="Available OpenStack Services")
ServiceAvailableGroup = [
    cfg.BoolOpt('congress',
                default=True,
                help="Whether or not Congress is expected to be available"),
]
congressha_group = cfg.OptGroup(name="congressha", title="Congress HA Options")

CongressHAGroup = [
    cfg.StrOpt("replica_type",
               default="policyha",
               help="service type used to create a replica congress server."),
    cfg.IntOpt("replica_port",
               default=4001,
               help="The listening port for a replica congress server. "),
]
