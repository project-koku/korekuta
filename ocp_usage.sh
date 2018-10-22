#!/bin/bash
#===============================================================================
#
#          FILE:  ocp_usage.sh
#
#         USAGE:  ./ocp_usage.sh
#
#   DESCRIPTION:  Setup and collect OCP usage data.
#
#       OPTIONS:  -h | --help   Obtain command USAGE
#                 -e | --extra-vars  set additional variables as key=value
#===============================================================================

export PATH=$PATH:$ANSIBLE_HOME/bin
PLAYBOOKFILE="ocp_usage_playbook.yml"
SETUP_TAG="--tags=setup"
COLLECT_TAG="--tags=collect"
tag=""

declare -a args
args=("$*")

set -- ${args[@]}

usage() {
    cat <<EOM
    Setup and collect OCP usage data.

    Usage:
    $(basename $0)

    Options:
    -h | --help   Obtain command USAGE
    (--setup | --collect) Run either the setup phase or collect phase
    -e | --extra-vars  Set additional variables as key=value


    Extra Variables:
    * Provide cluster alias:
         -e CLUSTER_ALIAS=MyCompanyProductionCluster
    * Provide Openshift Container Platform API Endpoint:
         -e OCP_API=api.openshift-prod.mycompany.com
    * Provide Openshift Container Platform User:
         -e OCP_USER=user
    * Provide Openshift Container Platform User Token File:
         -e OCP_TOKEN_PATH=/path/to/file/with/ocp/token
EOM
    exit 0
}

if [[ ($1 == "--help") ||  ($1 == "-h") ]]
then
  usage;
elif [[ ($1 == "--setup") ]]
then
  tag=$SETUP_TAG
elif [[ ($1 == "--collect") ]]
then
  tag=$COLLECT_TAG
else
  echo "Unexpected argument $1. Should be either --setup or --collect."
  exit 1
fi

# if [ ! -f /etc/redhat-release ]; then
#   echo '/etc/redhat-release not found. You need to run this on a Red Hat based OS.'
#   exit 1
# fi

if dnf --version > /dev/null 2>&1; then
  PKG_MGR=dnf
else
  PKG_MGR=yum
fi

echo 'Checking if ansible is installed...'
command -v ansible > /dev/null 2>&1

if [ $? -ne 0 ]
then
  echo 'Ansible prerequisite could not be found. Trying to install ansible...'
  ansible_not_installed=1
fi

if [ $ansible_not_installed ]; then
  sudo "${PKG_MGR}" install -y ansible
fi

command -v ansible > /dev/null 2>&1

if [ $? -ne 0 ]
then
  echo "Installation failed. Ansible prerequisite could not be installed."
  echo "Follow installation documentation for installing Ansible."
  exit 1
fi

echo ansible-playbook $PLAYBOOKFILE -v $tag ${@:2}
ansible-playbook $PLAYBOOKFILE -v $tag ${@:2}

if [ $? -eq 0 ]
then
  echo "Execution complete."
else
  echo "Execution failed. Review the install logs."
  exit $?
fi
