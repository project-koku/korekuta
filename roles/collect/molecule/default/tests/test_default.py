"""Tests for default molecule scenario."""

import io
import json
import os
import re

import testinfra.utils.ansible_runner


testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(  # pylint: disable=invalid-name
    os.environ["MOLECULE_INVENTORY_FILE"]
).get_hosts("all")

DOWNLOAD_PATH = "/tmp/korekuta-collect"
CLUSTER_ID = "bbb0b82b-e40d-41eb-8354-e07bc6a26a38"

# pylint: disable=line-too-long
UUID_RE = r"([a-fA-F0-9]{8}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{12})"
CSV_RE = r"([a-fA-F0-9]{8}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{12})_openshift_usage_report\.(\d+(_\d+)?)\.csv"  # noqa: E501
CSVHEADER = r"report_period_start,report_period_end,pod,namespace,node,resource_id,interval_start,interval_end"


def test_download_path(host):
    """Test download path."""
    assert host.file(DOWNLOAD_PATH).exists
    assert host.file(DOWNLOAD_PATH).is_directory
    assert host.file(f"{DOWNLOAD_PATH}/{CLUSTER_ID}").exists
    assert host.file(f"{DOWNLOAD_PATH}/{CLUSTER_ID}").is_directory


def test_csv_file(host):
    """Test that csv files with expected naming pattern exist and have a CSVHEADER."""
    list_dir = host.run(f"ls -1 {DOWNLOAD_PATH}/{CLUSTER_ID}/*.csv").stdout.split()
    assert len(list_dir) > 0
    for file_name in list_dir:
        assert re.search(CSV_RE, file_name)

        contents = io.StringIO(host.file(file_name).content_string)
        header = contents.readlines()[0]
        assert re.search(CSVHEADER, header)


def test_manifest_file(host):
    """Test manifest file and contents."""
    manifest_file = f"{DOWNLOAD_PATH}/{CLUSTER_ID}/manifest.json"
    assert host.file(manifest_file).exists
    assert host.file(manifest_file).is_file

    manifest = json.loads(host.file(manifest_file).content_string)
    for keyname in ["files", "date", "uuid", "cluster_id"]:
        assert keyname in manifest

    list_dir = host.run(f"ls -1 {DOWNLOAD_PATH}/{CLUSTER_ID}/*.csv").stdout.split()
    assert len(list_dir) > 0
    for file_name in list_dir:
        assert re.search(CSV_RE, file_name)
        assert os.path.basename(file_name) in manifest.get("files")

    assert re.match(UUID_RE, manifest.get("uuid"))
    assert manifest.get("cluster_id") == CLUSTER_ID


def test_archive_file(host):
    """Test archive file."""
    archive_re = r"korekuta(_\d+)?.tar.gz"
    list_dir = host.run(f"ls -1 {DOWNLOAD_PATH}/*.tar.gz").stdout.split()

    # files exist
    assert len(list_dir) > 0
    for file_name in list_dir:
        assert re.search(archive_re, file_name)
        assert host.file(file_name).size <= (1024 * 1024)
        tarfiles = host.run(f"tar -tf {DOWNLOAD_PATH}/{file_name}").stdout.split()
        for tfile in tarfiles:
            ext = tfile.split(".")[-1]
            assert ext in ["csv", "json"]
            if ext == "csv":
                assert re.search(CSV_RE, tfile)
            elif ext == "json":
                assert tfile == "manifest.json"
