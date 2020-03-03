#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright 2020 Red Hat, Inc.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
"""Create a tarball for metering reports downloaded from an OpenShift cluster."""

import argparse
import csv
import logging
import json
import os
import sys
import tarfile
from datetime import datetime
from uuid import uuid4


DEFAULT_MAX_SIZE = 100
MEGABYTE = 1024 * 1024

TEMPLATE = {
    "files": None,
    "date": datetime.utcnow().isoformat(),
    "uuid": str(uuid4()),
    "cluster_id": None
}


# the csv module doesn't expose the bytes-offset of the
# underlying file object.
#
# instead, the script estimates the size of the data as VARIANCE percent larger than a
# naïve string concatenation of the CSV fields to cover the overhead of quoting
# and delimiters. This gets close enough for now.
VARIANCE = 0.03

# Flag to use when writing to a file. Changed to "w" by the -o flag.
FILE_FLAG = "x"

# if we're creating more than 1k files, something is probably wrong.
MAX_SPLITS = 1000

# logging
LOG = logging.getLogger(__name__)
LOG_FORMAT = "%(asctime)s [%(levelname)s] %(message)s"
LOG_VERBOSITY = [logging.ERROR, logging.WARNING, logging.INFO, logging.DEBUG]
logging.basicConfig(format=LOG_FORMAT, level=logging.ERROR, stream=sys.stdout)


def parse_args():
    """Handle CLI arg parsing."""
    parser = argparse.ArgumentParser(description="Korekuta CSV file packaging script", prog=sys.argv[0])

    # required args
    parser.add_argument("-f", "--filepath", required=True, help="path to files to package")
    parser.add_argument(
        "-s",
        "--max-size",
        type=int,
        default=DEFAULT_MAX_SIZE,
        help=f"Maximum size of packages in MiB. (Default: {DEFAULT_MAX_SIZE} MiB)",
    )
    parser.add_argument(
        "-o", "--overwrite", action="store_true", default=False, help="whether to overwrite existing files."
    )
    parser.add_argument("--ocp-cluster-id", required=True, help="OCP Cluster ID")
    parser.add_argument("-v", "--verbosity", action="count", default=0, help="increase verbosity (up to -vvv)")
    return parser.parse_args()


def write_part(filename, csvreader, header, num=0, size=(DEFAULT_MAX_SIZE * MEGABYTE)):
    """Split a part of the file into a new file.

    Args:
        filename (str) name of original file
        csvreader (CSVReader) the csvreader object of original file
        header (list) the CSV file's header list
        num (int) the current split file index
        size (int) the maximum size of the split file in bytes

    Returns:
        (str) the name of the new split file
        (bool) whether the split reached the end of the csvreader

    """
    fname_part, ext = os.path.splitext(filename)
    size_estimate = 0
    split_filename = f"{fname_part}_{num}{ext}"
    try:
        with open(split_filename, FILE_FLAG) as split_part:
            LOG.info(f"Writing new file: {split_filename}")
            csvwriter = csv.writer(split_part)
            csvwriter.writerow(header)
            for row in csvreader:
                csvwriter.writerow(row)

                row_len = len(",".join(row))
                size_estimate += row_len + (row_len * VARIANCE)

                LOG.debug(f"file size (est): {size_estimate}")
                if size_estimate >= size:
                    return (split_filename, False)
    except (IOError, FileExistsError) as exc:
        LOG.critical(f"Fatal error: {exc}")
        sys.exit(2)
    return (split_filename, True)


def need_split(filepath, max_size):
    """Determine whether to split up the CSV files.

    Args:
        filepath (str) a directory
        max_size (int) maximum split size in MiB

    Returns:
        True if any single file OR the total sum of files exceeds the MAX_SIZE
        False if each single file AND the total file size is below MAX_SIZE

    """
    total_size = 0
    max_bytes = max_size * MEGABYTE
    for filename in os.listdir(filepath):
        this_size = os.stat(f"{filepath}/{filename}").st_size
        total_size += this_size
        if this_size >= max_bytes or total_size >= max_bytes:
            return True
    return False


def split_files(filepath, max_size):
    """Split any files that exceed the file size threshold.

    Args:
        filepath (str) file path containing the CSV files
        max_size (int) the maximum size in MiB for each file

    """
    for filename in os.listdir(filepath):
        abspath = f"{filepath}/{filename}"
        if os.stat(abspath).st_size >= max_size * MEGABYTE:
            csvheader = None
            split_files = []
            with open(abspath, "r") as fhandle:
                csvreader = csv.reader(fhandle)
                csvheader = next(csvreader)
                LOG.debug(f"Header: {csvheader}")

                part = 1
                while True:
                    newfile, eof = write_part(abspath, csvreader, csvheader, num=part, size=(max_size * MEGABYTE))
                    split_files.append(newfile)
                    part += 1
                    if eof or part >= MAX_SPLITS:
                        break

            os.remove(abspath)

            # return the list of split files to stdout
            LOG.info(f"Split files: {split_files}")


def render_manifest(args):
    """Render the manifest template and write it to a file.

    Args:
        args (Namespace) an ArgumentParser Namespace object

    Returns:
        (str) the rendered manifest file name
    """
    manifest = TEMPLATE
    manifest["cluster_id"] = args.ocp_cluster_id
    manifest["files"] = os.listdir(args.filepath)
    LOG.debug(f"rendered manifest: {manifest}")
    manifest_filename = f"{args.filepath}/manifest.json"

    if not os.path.exists(args.filepath):
        os.makedirs(args.filepath)
        LOG.info(f"Created dirs: {args.filepath}")

    try:
        with open(manifest_filename, FILE_FLAG) as mfile:
            json.dump(manifest, mfile)
    except FileExistsError as exc:
        LOG.critical(f"Fatal error: {exc}")
        sys.exit(2)
    LOG.info(f"manifest generated")
    return manifest_filename


def write_tarball(tarfilename, archivefiles=[]):
    """Write a tarball, adding the given files to the archive.

    Args:
        tarfilename (str) the name of the tarball to create
        archivefiles (list) the list of files to include in the archive

    Returns:
        (str) full filepath of the created tarball

    Raises:
        FileExistsError if tarfilename already exists
    """
    try:
        with tarfile.open(tarfilename, f"{FILE_FLAG}:gz") as tarball:
            for fname in archivefiles:
                LOG.debug(f"Adding {fname} to {tarfilename}: ")
                tarball.add(fname)
    except FileExistsError as exc:
        LOG.critical(exc)
        sys.exit(2)
    LOG.info(f"Wrote: {tarfilename}")
    return f"{tarfilename}"


if "__main__" in __name__:
    args = parse_args()
    if args.verbosity:
        LOG.setLevel(LOG_VERBOSITY[args.verbosity])
    LOG.debug("CLI Args: %s", args)

    if args.overwrite:
        FILE_FLAG = "w"

    out_files = []
    need_split = need_split(args.filepath, args.max_size)
    if need_split:
        split_files(args.filepath, args.max_size)
        manifest_filename = render_manifest(args)

        tarpath = args.filepath + "/../"
        tarfiletmpl = "korekuta_{}.tar.gz"
        for idx, filename in enumerate(os.listdir(args.filepath)):
            if ".csv" in filename:
                tarfilename = os.path.abspath(tarpath + tarfiletmpl.format(idx))
                out_files.append(write_tarball(tarfilename, [f"{args.filepath}/{filename}", manifest_filename]))
    else:
        render_manifest(args)
        tarfilename = os.path.abspath(args.filepath + "/../korekuta.tar.gz")
        out_files.append(write_tarball(tarfilename, [args.filepath]))

    for fname in out_files:
        print(fname)
