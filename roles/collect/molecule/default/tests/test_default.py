"""Tests for default molecule scenario."""
import os

import testinfra.utils.ansible_runner


testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(  # pylint: disable=invalid-name
    os.environ['MOLECULE_INVENTORY_FILE']).get_hosts('all')

download_path = '/tmp/korekuta-collect'  # pylint: disable=invalid-name


def test_download_path(host):
    """Test download path."""
    assert host.file(download_path).exists
    assert host.file(download_path).is_directory


def test_csv_file(host):
    """Test csv file."""
    csv_file = download_path + '/korekuta-collect-report.csv'
    assert host.file(csv_file).exists
    assert host.file(csv_file).is_file


def test_manifest_file(host):
    """Test manifest file and contents."""
    manifest_file = download_path + '/manifest.json'
    assert host.file(manifest_file).exists
    assert host.file(manifest_file).is_file
    assert host.file(manifest_file).contains(
        '"file": "korekuta-collect-report.csv"')
    assert host.file(manifest_file).contains('"date":')
    assert host.file(manifest_file).contains('"uuid":')
    assert host.file(manifest_file).contains('"cluster_id": "test-cluster-id"')


def test_archive_file(host):
    """Test archive file."""
    archive_file = '/tmp/korekuta.tar.bz2'
    assert host.file(archive_file).exists
    assert host.file(archive_file).is_file
