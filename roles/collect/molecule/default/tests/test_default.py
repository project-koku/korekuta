"""Tests for default molecule scenario."""
import json
import os

import testinfra.utils.ansible_runner


testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(  # pylint: disable=invalid-name
    os.environ['MOLECULE_INVENTORY_FILE']).get_hosts('all')

download_path = '/tmp/korekuta-collect'  # pylint: disable=invalid-name
cluster_id = 'bbb0b82b-e40d-41eb-8354-e07bc6a26a38'  # pylint: disable=invalid-name
collect_csv_uuid = 'd7449564-67a4-4507-86f2-db70055aa12a'


def test_download_path(host):
    """Test download path."""
    assert host.file(download_path).exists
    assert host.file(download_path).is_directory


def test_csv_file(host):
    """Test csv file."""
    test_files = ['{}_openshift_usage_report.0.csv'.format(cluster_id),
                  '{}_openshift_usage_report.1.csv'.format(cluster_id)]
    for file_name in test_files:
        csv_file = download_path + '/{}/{}'.format(cluster_id, file_name)
        assert host.file(csv_file).exists
        assert host.file(csv_file).is_file


def test_manifest_file(host):
    """Test manifest file and contents."""
    test_files = ['{}_openshift_usage_report.0.csv'.format(cluster_id),
                  '{}_openshift_usage_report.1.csv'.format(cluster_id)]
    manifest_file = download_path + '/{}'.format(cluster_id) + '/manifest.json'
    assert host.file(manifest_file).exists
    assert host.file(manifest_file).is_file
    manifest = json.loads(host.file(manifest_file).content_string)
    for keyname in ['files', 'date', 'uuid', 'cluster_id']:
        assert keyname in manifest
    for file_name in test_files:
        assert file_name in manifest.get('files')
    assert manifest.get('uuid') == collect_csv_uuid
    assert manifest.get('cluster_id') == cluster_id


def test_archive_file(host):
    """Test archive file."""
    archive_file = '/tmp/korekuta.tar.bz2'
    assert host.file(archive_file).exists
    assert host.file(archive_file).is_file
