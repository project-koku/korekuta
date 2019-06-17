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
BASEDIR=$(dirname "$0")
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
    * Provide OpenShift Container Platform API Endpoint:
         -e OCP_API=https://api.openshift-prod.mycompany.com
    * Provide OpenShift Container Platform User Token File:
         -e OCP_TOKEN_PATH=/path/to/file/with/ocp/token
    * Provide OpenShift Metering Namespace:
         -e OCP_METERING_NAMESPACE=metering
    * Provide OpenShift Container Platform CLI (defaults to /usr/bin/oc):
         -e OCP_CLI=/usr/local/bin/oc
    * Provide OpenShift Proxy Port (defaults to 8001):
         -e OCP_PROXY_PORT=8001
    * Validate OpenShift SSL Certifates  (defaults to false):
         -e OCP_SSL_CERT_VALIDATION=false
    * Provide OpenShift Cluster Identifier:
         -e OCP_CLUSTER_ID=bbb0b82b-e40d-41eb-8354-e07bc6a26a38
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

echo ansible-playbook $BASEDIR/$PLAYBOOKFILE -v $tag ${@:2}
ansible-playbook $BASEDIR/$PLAYBOOKFILE -v $tag ${@:2}

if [ $? -eq 0 ]
then
  echo "Execution complete."
else
  echo "Execution failed. Review the install logs."
  exit $?
fi
