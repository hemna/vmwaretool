# Copyright (c) 2015 VMware, Inc.
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

"""
Exception definitions.
"""

from oslo_vmware import exceptions


class InvalidAdapterTypeException(exceptions.VMwareDriverException):
    """Thrown when the disk adapter type is invalid."""
    msg_fmt = ("Invalid disk adapter type: %(invalid_type)s.")


class InvalidDiskTypeException(exceptions.VMwareDriverException):
    """Thrown when the disk type is invalid."""
    msg_fmt = ("Invalid disk type: %(disk_type)s.")


class VirtualDiskNotFoundException(exceptions.VMwareDriverException):
    """Thrown when virtual disk is not found."""
    msg_fmt = ("There is no virtual disk device.")


class ProfileNotFoundException(exceptions.VMwareDriverException):
    """Thrown when the given storage profile cannot be found."""
    msg_fmt = ("Storage profile: %(storage_profile)s not found.")


class NoValidDatastoreException(exceptions.VMwareDriverException):
    """Thrown when there are no valid datastores."""
    msg_fmt = ("There are no valid datastores.")


class ClusterNotFoundException(exceptions.VMwareDriverException):
    """Thrown when the given cluster cannot be found."""
    msg_fmt = ("Compute cluster: %(cluster)s not found.")


class NoValidHostException(exceptions.VMwareDriverException):
    """Thrown when there are no valid ESX hosts."""
    msg_fmt = ("There are no valid ESX hosts.")


class TemplateNotFoundException(exceptions.VMwareDriverException):
    """Thrown when template cannot be found."""
    msg_fmt = ("Template cannot be found at path: %(path)s.")


class SnapshotNotFoundException(exceptions.VMwareDriverException):
    """Thrown when the backend snapshot cannot be found."""
    msg_fmt = ("Snapshot: %(name)s not found.")
