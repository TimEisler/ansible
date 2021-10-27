#!/usr/bin/env bash

set -eux

ansible-playbook test_includes.yml -i ../../inventory "$@"

ansible-playbook inherit_notify.yml "$@"

echo "EXPECTED ERROR: Ensure we fail if using 'include' to include a playbook."
set +e
result="$(ansible-playbook -i ../../inventory include_on_playbook_should_fail.yml -v "$@" 2>&1)"
set -e
grep -q "ERROR! 'include' is not a valid attribute for a Play" <<< "$result"

ANSIBLE_ROLES_PATH=../ ansible-playbook setup.yml

ANSIBLE_NOCOLOR=1
export ANSIBLE_NOCOLOR
env python test_include_task_reverse.py "$@"

ansible-playbook ./include_task_reverse.yml --syntax-check -i ../../inventory -v "$@"

