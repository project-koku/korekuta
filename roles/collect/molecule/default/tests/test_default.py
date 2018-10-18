import os

import testinfra.utils.ansible_runner

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']).get_hosts('all')

download_path = '/tmp/korekuta-collect'


def test_download_path(host):
    assert host.file(download_path).exists
    assert host.file(download_path).is_directory


def test_csv_file(host):
    csv_file = download_path + '/korekuta-collect-report.csv'
    assert host.file(csv_file).exists
    assert host.file(csv_file).is_file


def test_manifest_file(host):
    manifest_file = download_path + '/manifest.json'
    assert host.file(manifest_file).exists
    assert host.file(manifest_file).is_file


def test_archive_file(host):
    archive_file = '/tmp/korekuta.tar.bz2'
    assert host.file(archive_file).exists
    assert host.file(archive_file).is_file
