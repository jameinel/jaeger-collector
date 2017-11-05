import json
import os
import shutil

from charmhelpers import fetch
from charmhelpers.core import hookenv, host
from charmhelpers.core.templating import render
from charms.reactive import when, when_not, is_state, set_state

@when_not('jaeger-collector.installed')
def install_jaeger_collector():
    # Do your setup here.
    #
    # If your charm has other dependencies before it can install,
    # add those as @when() clauses above., or as additional @when()
    # decorated handlers below
    #
    # See the following for information about reactive charms:
    #
    #  * https://jujucharms.com/docs/devel/developer-getting-started
    #  * https://github.com/juju-solutions/layer-basic#overview
    #
    hookenv.status_set('maintenance', 'installing')
    ensure_jaeger_directory()
    hookenv.status_set('blocked', 'waiting for cassandra') # TODO: elasticsearch')
    set_state('jaeger-collector.installed')


runtimePath = '/var/lib/jaeger-collector'

def ensure_jaeger_directory():
    os.makedirs(runtimePath, mode=770)
    execPath = os.path.join(runtimePath, "jaeger-collector")
    # TODO: jam 2017-11-05 Ultimately we should be installing from somewhere
    #       else, and making sure the right version is available. Until then, we should
    #       also make sure that the version of the binary that we want to run matches.
    if not os.path.exists(execPath):
        os.symlink(os.path.abspath("jaeger-collector"), execPath)
    targetShell = os.path.join(runtimePath, "jaeger-collector.sh")
    configPath = os.path.join(runtimePath, "config.yaml")
    render(source="jaeger-collector.sh",
            target=targetShell,
            context={
                config_path=configPath,
                exec_path=execPath,
            },
    )
    os.chmod(targetShell, 0750)

# Some config entries are just mapped directly through to the config script
_config_mapping = {
        "cassandra-connections-per-host": "cassandra.connections-per-host",
        "cassandra-replicationfactor": "cassandra.replicationfactor",
        "collector-num-workers": "collector.num-workers",
}

def maybe_restart_collector():
    """Restart the collector (new config), but only if it was already started"""
    if not is_state("jaeger-collector.started"):
        return
    host.service_restart("jaeger-collector")


def serviceConfigFilename():
    return os.path.join(runtimePath, "config.json")


@when("config.changed", "cassandra.available")
def rebuild_config(cassandra):
    config = hookenv.config()
    out_config = {}
    for k, v in config.items():
        if k in _config_mapping:
            outkey = _config_mapping[k].split('.')
            section = out_config
            for nextkey in range outkey[:-1]:
                section = out_config.setdefault(nextkey, {})
            section[outkey[-1]] = v
    cassandraconf = out_config.setdefault("cassandra", {})


@when("jaeger-collector.start")
@when_not("jaeger-collector.started")
def ensure_jaeger_service():
    # We wait to start the service until we have been connected to either
    # Cassandra or Elasticsearch, and the configuration file has been written.
    servicePath = "/etc/systemd/system/jaeger-collector.service"
    if not os.path.exists(servicePath):
        render(source="jaeger-collector.service",
                target=servicePath,
                context={
                },
        )
    if not host.service_start('jaeger-collector'):
        # TODO: jam 2017-11-05 turn this into a logging call at higher urgency
        print("Failed to start service jaeger-collector")
        hookenv.set_status('blocked', 'failed to start service jaeger-collector')
    else:
        set_state('jaeger-collector.started')
        hookenv.set_status('active', 'jaeger-collector started')


def ensure_cassandra_libs():
    hookenv.set_status('maintenance', 'installing cassandra packages')
    fetch.apt_install(fetch.filter_installed_packages(['python3-cassandra']))


@when('cassandra.available')
def connect_to_cassandra(cassandra):
    for unit in cassandra.list_unit_data():
        print(unit)
    ensure_jaeger_directory()
    # TODO: jam 2017-11-05 deal with config that asks us to set up a KEYSPACE
    # in Cassandra
    set_state('jaeger-collector.start')
