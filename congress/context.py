# Copyright 2012 OpenStack Foundation.
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

"""RequestContext: context for requests that persist through congress."""
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import

import copy
import datetime

from oslo_context import context as common_context
from oslo_log import log as logging

from congress.common import policy


LOG = logging.getLogger(__name__)


class RequestContext(common_context.RequestContext):
    """Security context and request information.

    Represents the user taking a given action within the system.

    """

    def __init__(self, user_id, tenant_id, is_admin=None, read_deleted="no",
                 roles=None, timestamp=None, load_admin_roles=True,
                 request_id=None, tenant_name=None, user_name=None,
                 overwrite=True, **kwargs):
        """Object initialization.

        :param read_deleted: 'no' indicates deleted records are hidden, 'yes'
            indicates deleted records are visible, 'only' indicates that
            *only* deleted records are visible.

        :param overwrite: Set to False to ensure that the greenthread local
            copy of the index is not overwritten.

        :param kwargs: Extra arguments that might be present, but we ignore
            because they possibly came in from older rpc messages.
        """
        super(RequestContext, self).__init__(user=user_id, tenant=tenant_id,
                                             is_admin=is_admin,
                                             request_id=request_id,
                                             overwrite=overwrite,
                                             roles=roles)
        self.user_name = user_name
        self.tenant_name = tenant_name

        self.read_deleted = read_deleted
        if not timestamp:
            timestamp = datetime.datetime.utcnow()
        self.timestamp = timestamp
        self._session = None
        if self.is_admin is None:
            self.is_admin = policy.check_is_admin(self)

        # Log only once the context has been configured to prevent
        # format errors.
        if kwargs:
            LOG.debug(_('Arguments dropped when creating '
                        'context: %s'), kwargs)

    @property
    def project_id(self):
        return self.tenant

    @property
    def tenant_id(self):
        return self.tenant

    @tenant_id.setter
    def tenant_id(self, tenant_id):
        self.tenant = tenant_id

    @property
    def user_id(self):
        return self.user

    @user_id.setter
    def user_id(self, user_id):
        self.user = user_id

    def _get_read_deleted(self):
        return self._read_deleted

    def _set_read_deleted(self, read_deleted):
        if read_deleted not in ('no', 'yes', 'only'):
            raise ValueError(_("read_deleted can only be one of 'no', "
                               "'yes' or 'only', not %r") % read_deleted)
        self._read_deleted = read_deleted

    def _del_read_deleted(self):
        del self._read_deleted

    read_deleted = property(_get_read_deleted, _set_read_deleted,
                            _del_read_deleted)

    def to_dict(self):
        ret = super(RequestContext, self).to_dict()
        ret.update({'user_id': self.user_id,
                    'tenant_id': self.tenant_id,
                    'project_id': self.project_id,
                    'read_deleted': self.read_deleted,
                    'timestamp': str(self.timestamp),
                    'tenant_name': self.tenant_name,
                    'project_name': self.tenant_name,
                    'user_name': self.user_name})
        return ret

    @classmethod
    def from_dict(cls, values):
        return cls(**values)

    def elevated(self, read_deleted=None):
        """Return a version of this context with admin flag set."""
        context = copy.copy(self)
        context.is_admin = True

        if 'admin' not in [x.lower() for x in context.roles]:
            context.roles.append('admin')

        if read_deleted is not None:
            context.read_deleted = read_deleted

        return context


def get_admin_context(read_deleted="no", load_admin_roles=True):
    return RequestContext(user_id=None,
                          tenant_id=None,
                          is_admin=True,
                          read_deleted=read_deleted,
                          load_admin_roles=load_admin_roles,
                          overwrite=False)
