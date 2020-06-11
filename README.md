# korekuta

The korekuta repository is now read-only and will not receive additional updates. Please see the newer korekuta-operator which is now being maintained in korekuta's place. https://github.com/project-koku/korekuta-operator

## About
Data collector tool to obtain OCP usage data and upload it to masu. The data collector tool utilizes [ansible](https://www.ansible.com/) to collect usage data from an OCP cluster installation.

## Development

This is a Python project developed using Python 3.6. Make sure you have at least this version installed.

To get started developing against Korekuta first clone a local copy of the git repository.

```
git clone https://github.com/project-koku/korekuta
```

Developing inside a virtual environment is recommended. A Pipfile is provided. Pipenv is recommended for combining virtual environment (virtualenv) and dependency management (pip).

To install pipenv, use pip

```
pip3 install pipenv
```

Then project dependencies and a virtual environment can be created using

```
pipenv install --dev
```

**NOTE:** For Linux systems, use `pipenv --site-packages` or `mkvirtualenv --system-site-packages` to set up the virtual environment. Ansible requires access to libselinux-python, which should be installed system-wide on most distributions.

To activate the virtual environment run

```
pipenv shell
```

## Testing

We utilize [molecule](https://molecule.readthedocs.io/en/latest/) to test the ansible roles.

Change directory to the role to be tested and run molecule (example below with setup role):

```
cd roles/setup
molecule test
```

There are two Molecule scenarios for each role two support both the Docker and
Podman container drivers.

To run a particular scenario, use molecule's `-s` flag:

```
molecule test -s <scenario>
```
