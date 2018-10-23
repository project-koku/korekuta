"""Tests for default molecule scenario."""

import os

import testinfra.utils.ansible_runner


testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(  # pylint: disable=invalid-name
    os.environ['MOLECULE_INVENTORY_FILE']).get_hosts('all')

CONFIG_DIRECTORY = '/root/.config/ocp_usage'


def test_config_directory(host):
    """Test config path."""
    assert host.file(CONFIG_DIRECTORY).exists
    assert host.file(CONFIG_DIRECTORY).is_directory


def test_manifest_file(host):
    """Test config file and contents."""
    config_file = CONFIG_DIRECTORY + '/config.json'
    assert host.file(config_file).exists
    assert host.file(config_file).is_file
    assert host.file(config_file).contains(
        '"ocp_api": "http://127.0.0.1:8443"')
    assert host.file(config_file).contains('"ocp_user":')
    assert host.file(config_file).contains('"ocp_token_file":')
    assert host.file(config_file).contains('"cluster_id":')
    assert host.file(config_file).contains('"ocp_metering_namespace":')
