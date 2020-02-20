Korekuta Setup
=========

Prepare an OpenShift 3.x cluster for retrieving metering reports.

Requirements
------------

Korekuta Setup role needs to run before the Collect role.

Example Playbook
----------------

    - hosts: servers
      roles:
         - { role: setup }

License
-------

AGPL-3.0

Author Information
------------------

Red Hat, Inc.
