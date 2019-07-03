"""Tests for default molecule scenario."""

import os

import testinfra.utils.ansible_runner


testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(  # pylint: disable=invalid-name
    os.environ['MOLECULE_INVENTORY_FILE']).get_hosts('all')

CONFIG_DIRECTORY = '/root/.config/ocp_usage/bbb0b82b-e40d-41eb-8354-e07bc6a26a38/'


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
        '"ocp_api": "http://127.0.0.1:8001"')
    assert host.file(config_file).contains('"ocp_token_file":')
    assert host.file(config_file).contains('"ocp_cluster_id":')
    assert host.file(config_file).contains('"ocp_metering_namespace":')
    assert host.file(config_file).contains('"ocp_cli":')
    assert host.file(config_file).contains('"ocp_validate_cert":')
    assert host.file(config_file).contains('"metering_api":')
