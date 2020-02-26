Korekuta Collect
=========

Collect metering report files from an OpenShift cluster.

Requirements
------------

Korekuta Setup role needs to run first.

Role Variables
--------------

collect_archive_filename: the filename of the tarball extracted from the cluster.

Example Playbook
----------------

    - hosts: servers
      roles:
         - { role: collect }

License
-------

AGPL-3.0

Author Information
------------------

Red Hat, Inc.
