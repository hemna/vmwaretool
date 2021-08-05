
from oslo_config import cfg
from oslo_log import log as logging
from oslo_vmware import api
from oslo_vmware import exceptions
from oslo_vmware import image_transfer
from oslo_vmware import pbm
from oslo_vmware import vim_util

from vmwaretool import volumeops

EXTENSION_KEY = 'org.openstack.storage'
EXTENSION_TYPE = 'volume'


vmdk_opts = [
    cfg.StrOpt('vmware_host_ip',
               help='IP address for connecting to VMware vCenter server.'),
    cfg.PortOpt('vmware_host_port',
                default=443,
                help='Port number for connecting to VMware vCenter server.'),
    cfg.StrOpt('vmware_host_username',
               help='Username for authenticating with VMware vCenter '
                    'server.'),
    cfg.StrOpt('vmware_host_password',
               help='Password for authenticating with VMware vCenter '
                    'server.',
               secret=True),
    cfg.StrOpt('vmware_wsdl_location',
               help='Optional VIM service WSDL Location '
                    'e.g http://<server>/vimService.wsdl. Optional over-ride '
                    'to default location for bug work-arounds.'),
    cfg.IntOpt('vmware_api_retry_count',
               default=10,
               help='Number of times VMware vCenter server API must be '
                    'retried upon connection related issues.'),
    cfg.FloatOpt('vmware_task_poll_interval',
                 default=2.0,
                 help='The interval (in seconds) for polling remote tasks '
                      'invoked on VMware vCenter server.'),
    cfg.StrOpt('vmware_volume_folder',
               default='Volumes',
               help='Name of the vCenter inventory folder that will '
                    'contain Cinder volumes. This folder will be created '
                    'under "OpenStack/<project_folder>", where project_folder '
                    'is of format "Project (<volume_project_id>)".'),
    cfg.IntOpt('vmware_image_transfer_timeout_secs',
               default=7200,
               help='Timeout in seconds for VMDK volume transfer between '
                    'Cinder and Glance.'),
    cfg.IntOpt('vmware_max_objects_retrieval',
               default=100,
               help='Max number of objects to be retrieved per batch. '
                    'Query results will be obtained in batches from the '
                    'server and not in one shot. Server may still limit the '
                    'count to something less than the configured value.'),
    cfg.StrOpt('vmware_host_version',
               help='Optional string specifying the VMware vCenter server '
                    'version. '
                    'The driver attempts to retrieve the version from VMware '
                    'vCenter server. Set this configuration only if you want '
                    'to override the vCenter server version.'),
    cfg.StrOpt('vmware_tmp_dir',
               default='/tmp',
               help='Directory where virtual disks are stored during volume '
                    'backup and restore.'),
    cfg.StrOpt('vmware_ca_file',
               help='CA bundle file to use in verifying the vCenter server '
                    'certificate.'),
    cfg.BoolOpt('vmware_insecure',
                default=False,
                help='If true, the vCenter server certificate is not '
                     'verified. If false, then the default CA truststore is '
                     'used for verification. This option is ignored if '
                     '"vmware_ca_file" is set.'),
    cfg.MultiStrOpt('vmware_cluster_name',
                    help='Name of a vCenter compute cluster where volumes '
                         'should be created.'),
    cfg.MultiStrOpt('vmware_storage_profile',
                    help='Names of storage profiles to be monitored.',
                    deprecated_for_removal=True,
                    deprecated_reason='Setting this option results in '
                                      'significant performance degradation.'),
    cfg.IntOpt('vmware_connection_pool_size',
               default=10,
               help='Maximum number of connections in http connection pool.'),
    cfg.StrOpt('vmware_adapter_type',
               choices=[volumeops.VirtualDiskAdapterType.LSI_LOGIC,
                        volumeops.VirtualDiskAdapterType.BUS_LOGIC,
                        volumeops.VirtualDiskAdapterType.LSI_LOGIC_SAS,
                        volumeops.VirtualDiskAdapterType.PARA_VIRTUAL,
                        volumeops.VirtualDiskAdapterType.IDE],
               default=volumeops.VirtualDiskAdapterType.LSI_LOGIC,
               help='Default adapter type to be used for attaching volumes.'),
    cfg.StrOpt('vmware_snapshot_format',
               choices=['template', 'COW'],
               default='template',
               help='Volume snapshot format in vCenter server.'),
    cfg.BoolOpt('vmware_lazy_create',
                default=True,
                help='If true, the backend volume in vCenter server is created'
                     ' lazily when the volume is created without any source. '
                     'The backend volume is created when the volume is '
                     'attached, uploaded to image service or during backup.'),
    cfg.StrOpt('vmware_datastore_regex',
               help='Regular expression pattern to match the name of '
                    'datastores where backend volumes are created.'),
    cfg.BoolOpt('vmware_online_resize',
                default=True,
                help='If true, enables volume resize in in-use state'),
    cfg.BoolOpt('vmware_profile_check_on_attach',
                default=True,
                help='If False, we are not checking the storage-policy in '
                'case of attach operation for an existing backing. This is '
                'required to allow DS maintanance, where we remove the '
                'storage-profile to prohibit cinder from scheduling new '
                'volumes to that DS and move the volumes away manually. '
                'Not disabling this would mean cinder moves the volumes '
                'around, which can take a long time and leads to timeouts.'),
    cfg.BoolOpt('vmware_select_random_best_datastore',
                default=False,
                help='If True, driver will randomize the picking of '
                'best datastore from best possible datastores '
                'during volume backing creation.  Best possible datastores '
                'are most connected hosts and most free space.'),
    cfg.IntOpt('vmware_random_datastore_range',
               default=None,
               help='If vmware_select_random_best_datastore is enabled '
               'this enables subselecting a range of datastores to pick from '
               'after they have been sorted.  ie.  If there are 10 '
               'datastores, and vmware_random_datastore_range is set to 5 '
               'Then it will filter in 5 datastores prior to randomizing '
               'the datastores to pick from.'),
]

CONF = cfg.CONF
CONF.register_opts(vmdk_opts, group='vmware')


def _create_session():
    ip = CONF.vmware.vmware_host_ip
    port = CONF.vmware.vmware_host_port
    username = CONF.vmware.vmware_host_username
    password = CONF.vmware.vmware_host_password
    api_retry_count = CONF.vmware.vmware_api_retry_count
    task_poll_interval = CONF.vmware.vmware_task_poll_interval
    wsdl_loc = CONF.vmware.get('vmware_wsdl_location', None)
    ca_file = CONF.vmware.vmware_ca_file
    insecure = CONF.vmware.vmware_insecure
    pool_size = CONF.vmware.vmware_connection_pool_size
    session = api.VMwareAPISession(ip,
                                   username,
                                   password,
                                   api_retry_count,
                                   task_poll_interval,
                                   wsdl_loc=wsdl_loc,
                                   port=port,
                                   cacert=ca_file,
                                   insecure=insecure,
                                   pool_size=pool_size,
                                   op_id_prefix='c-vol')
    return session


def setup_connection():
    session = _create_session()
    max_objects = CONF.vmware.vmware_max_objects_retrieval
    random_ds = CONF.vmware.vmware_select_random_best_datastore
    random_ds_range = CONF.vmware.vmware_random_datastore_range
    _volumeops = volumeops.VMwareVolumeOps(session, max_objects, EXTENSION_KEY, EXTENSION_TYPE)

    return (session, _volumeops)
