# -*- coding: utf-8 -*-

# Copyright:  Ansible Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type


DOCUMENTATION = r'''
---
author: Ansible Core Team (@ansible)
module: include_tasks
short_description: Dynamically include a task list
description:
  - Includes a file with a list of tasks to be executed in the current playbook.
version_added: '2.4'
options:
  file:
    description:
      - The name of the imported file is specified directly without any other option.
      - Unlike M(ansible.builtin.import_tasks), most keywords, including loop, with_items, and conditionals, apply to this statement.
      - The do until loop is not supported on M(ansible.builtin.include_tasks).
    type: str
    version_added: '2.7'
  apply:
    description:
      - Accepts a hash of task keywords (e.g. C(tags), C(become)) that will be applied to the tasks within the include.
    type: str
    version_added: '2.7'
  reverse:
    description:
      - Reverse the tasks defined in the included yml file so that rescue and block can use the same file.
      - The included yml file needs to be written so that the task smake sense for block and the reversed tasks make sense for rescue.
      - See EXAMPLES below.
    type: bool
    version_added: 'tbd'
  free-form:
    description:
      - |
        Supplying a file name via free-form C(- include_tasks: file.yml) of a file to be included is the equivalent
        of specifying an argument of I(file).
extends_documentation_fragment:
    - action_common_attributes
    - action_common_attributes.conn
    - action_common_attributes.flow
    - action_core
    - action_core.include
attributes:
    check_mode:
        support: none
    diff_mode:
        support: none
seealso:
- module: ansible.builtin.import_playbook
- module: ansible.builtin.import_role
- module: ansible.builtin.import_tasks
- module: ansible.builtin.include_role
- ref: playbooks_reuse_includes
  description: More information related to including and importing playbooks, roles and tasks.
'''

EXAMPLES = r'''
- hosts: all
  tasks:
    - ansible.builtin.debug:
        msg: task1

    - name: Include task list in play
      ansible.builtin.include_tasks: stuff.yaml

    - ansible.builtin.debug:
        msg: task10

- hosts: all
  tasks:
    - ansible.builtin.debug:
        msg: task1

    - name: Include task list in play only if the condition is true
      ansible.builtin.include_tasks: "{{ hostvar }}.yaml"
      when: hostvar is defined

- name: Apply tags to tasks within included file
  ansible.builtin.include_tasks:
    file: install.yml
    apply:
      tags:
        - install
  tags:
    - always

- name: Apply tags to tasks within included file when using free-form
  ansible.builtin.include_tasks: install.yml
  args:
    apply:
      tags:
        - install
  tags:
    - always

- name: Execute tasks in the included file in the order written for block but in reverse order for rescue.
- hosts: all
  gather_facts: yes
  vars:
    pip_pkgname: 'bottle'
    path: '/usr/local/{{ pip_pkgname }}'
    marker_file_name: '{{ pip_pkgname }}_installed.txt'

  tasks:
    - block:
      - name: Block. Reversal is not expected
        include_tasks:
          file: ./shared_task_file.yml
      rescue:
      - name: Rescue. Reversal is expected
        include_tasks:
          file: ./shared_task_file.yml
          reverse: true
          apply:
            vars:
              - state: absent

shared_task_file.yml for the playbook above:
- name: Task 1 - Display starting install message.
  debug:
    msg: "Starting installation of the {{ pip_pkgname }} Python package."
  when: ansible_failed_result is not defined

- name: Task 2 - Check marker file
  stat:
    path: "{{ path }}/{{ marker_file_name }}"
  register: marker_file

- name: Task 3 - Manage the pip pkg as directed by the play.
  ansible.builtin.pip:
    name: "{{ pip_pkgname }}"
    state: "{{ state | default('present') }}"
  become: true
  register: result_pip

- name: Task 4 - Manage marker directory.
  ansible.builtin.file:
    path: "{{ path }}"
    state: "{{ state | default('directory') }}"
  become: true
  when: ansible_failed_result is defined or (result_pip.failed is defined and not result_pip.failed)

- name: Task 5 - Manage marker file
  ansible.builtin.file:
    path: "{{ path }}/{{ marker_file }}"
    state: "{{ state | default('touch') }}"
  become: true
  when: ansible_failed_result is defined or (not marker_file.stat.exists and result_pip.failed is defined and not result_pip.failed)

- name: Test case - Cause a failure in block
  fail:
  when: ansible_failed_result is not defined

- name: Task 6 - Display starting rescue message.
  debug:
    msg: "Starting rescue of the failed installation of the {{ pip_pkgname }} Python package."
  when: ansible_failed_result is defined
'''

RETURN = r'''
# This module does not return anything except tasks to execute.
'''
