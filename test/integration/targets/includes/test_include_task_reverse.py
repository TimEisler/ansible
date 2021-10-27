#!/usr/bin/env python
# Based on ~/ansible/test/integration/targets/cli/test_k_and_K.py
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

# Use -vvv to see much more detail.

# Make coding more python3-ish
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import os
import pexpect
import re
import sys

os.environ['ANSIBLE_NOCOLOR'] = '1'

#  Run the play and capture the output:
rawout = pexpect.run('ansible-playbook ./include_task_reverse.yml',timeout=10)

# I get ANSI codes even with ANSIBLE_NOCOLOR=1. This is thanks to https://stackoverflow.com/questions/14693701/how-can-i-remove-the-ansi-escape-sequences-from-a-string-in-python
ansi_escape = re.compile(b'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
out = ansi_escape.sub(b'', rawout)

if out and '-vvv' in sys.argv[1:]:
    print(f'pexpect has captured the following output: {out}')

# Pattern 1: Check to see if the block section includes the tasks, that they are not reversed, that an expected failure occurs before all 4 included tasks are run, and that the rescue section starts:
# Wed Oct 27 02:00:11 PM CDT 2021 TO CONSIDER: match the msg more precisely:     "msg": "Starting installation of the bottle Python package."\r\n
seq_check_1 = re.search(b'(PLAY \[\S+\]).+?(\r\n){1,2}(TASK \[Gathering Facts\]).+?\r\n(ok.+)(\r\n){1,2}(TASK \[Block. Failure is expected\]).+?\r\n(included:.+?for \S+)(\r\n){1,2}(TASK \[Task 1 - Display starting install message\.\]).+\r\n(ok.+)\r\n(.+msg.+)\r\n\}\r\n\r\n(TASK \[Task 2 - Cause a failure\]).+?\r\n(fatal:.+Failed as requested from task.+)\r\n\r\n(TASK \[Rescue. Reversal is expected\])', out)

if seq_check_1 and '-vvv' in sys.argv[1:]:
  print (f'A match was found for the first pattern at {seq_check_1.start()}-{seq_check_1.end()}: {seq_check_1.group()}')
  print(f'{seq_check_1.lastindex} groups were extracted.')
  for i in range(seq_check_1.lastindex+1):
    print(f'Group {i}: {seq_check_1.group(i)}')

# Pattern 2: Check to see if the rescue section includes the tasks, that they *are* reversed, that no failure occurs, and all 4 included tasks are run (some will be skipped), and that the always section starts:
# Wed Oct 27 02:00:11 PM CDT 2021 TO CONSIDER: match the msg more precisely:     "msg": "Starting rescue of the failed installation of the bottle Python package."\r\n
seq_check_2 = re.search(b'(TASK \[Rescue. Reversal is expected\]).+?\r\n(included:.+?for \S+ \(reversed\))(\r\n){1,2}(TASK \[Task 4 - Display starting rescue message\.\]).+\r\n(ok.+)\r\n(.+msg.+)\r\n\}\r\n\r\n(TASK \[Task 3.+\]).+\r\n(ok.+)(\r\n){1,2}(TASK \[Task 2.+\]).+\r\n(skipping.+)\r\n\r\n(TASK \[Task 1 - Display starting install message\.\]).+\r\n(skipping.+)\r\n\r\n(TASK \[Always. Reversal is not expected\])', out)

if seq_check_2 and '-vvv' in sys.argv[1:]:
  print (f'A match was found for the second pattern at {seq_check_2.start()}-{seq_check_2.end()}: {seq_check_2.group()}')
  print(f'{seq_check_2.lastindex} groups were extracted.')
  for i in range(seq_check_2.lastindex+1):
    print(f'Group {i}: {seq_check_2.group(i)}')

# Pattern 3: Check to see if the always section includes the tasks, that they are not reversed, that no failure occurs, and all 4 included tasks are run (some will be skipped), and that the always section starts:
# Wed Oct 27 3:30 PM CDT 2021 TO DO: add checks for 'Post-task assertions', and also the PLAY RECAP at the very end.
# Wed Oct 27 02:00:11 PM CDT 2021 TO CONSIDER: match the msg more precisely:     "msg": "Checking installation of the bottle Python package."\r\n
seq_check_3 = re.search(b'(TASK \[Always. Reversal is not expected\]).+?\r\n(included:.+?for \S+)(\r\n){1,2}(TASK \[Task 1 - Display a progress message\.\]).+\r\n(ok.+)\r\n(.+msg.+)\r\n\}\r\n\r\n(TASK \[Task 2 - Check the installation status .+\]).+?\r\n(ok.+)(\r\n){1,2}(TASK \[Task 3 - Prepare the output.+\]).+\r\n(ok.+)(\r\n){1,2}(TASK \[Post-task assertions\.\]).+\r\n(ok.+)\r\n(.+changed.+)\r\n(    "msg": "All assertions passed")\r\n\}\r\n\r\n(PLAY RECAP).+\r\n(\S+\s+: ok=11   changed=0    unreachable=0    failed=0    skipped=2    rescued=1    ignored=0).+\r\n\r\n', out)

if seq_check_3 and '-vvv' in sys.argv[1:]:
  print (f'A match was found for the third pattern at {seq_check_3.start()}-{seq_check_3.end()}: {seq_check_3.group()}')
  print(f'{seq_check_3.lastindex} groups were extracted.')
  for i in range(seq_check_3.lastindex+1):
    print(f'Group {i}: {seq_check_3.group(i)}')

assert seq_check_1 is not None
assert seq_check_2 is not None
assert seq_check_3 is not None

print("All assertions passed.")
