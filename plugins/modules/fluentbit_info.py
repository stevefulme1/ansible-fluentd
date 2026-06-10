#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2024, Steve Fulmer (@stevefulme1)
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
---
module: fluentbit_info
short_description: Gather Fluent Bit installation information
version_added: "0.1.0"
description:
  - Returns information about the installed Fluent Bit instance including
    version and binary path.
  - This is an info module and never reports C(changed).
options:
  fluentbit_bin:
    description:
      - Path to the C(fluent-bit) binary.
      - Auto-detected when omitted.
    type: path
author:
  - Steve Fulmer (@stevefulme1)
"""

EXAMPLES = r"""
- name: Get fluent-bit installation info
  stevefulme1.fluentd.fluentbit_info:
  register: result

- name: Display fluent-bit version
  ansible.builtin.debug:
    msg: "Fluent Bit version {{ result.version }}"
"""

RETURN = r"""
version:
  description: Installed Fluent Bit version.
  returned: always
  type: str
  sample: "3.0.4"
binary_path:
  description: Path to the fluent-bit binary.
  returned: always
  type: str
  sample: "/usr/sbin/fluent-bit"
"""

import re

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.stevefulme1.fluentd.plugins.module_utils.fluentd_common import (
    find_fluentbit_binary,
)


def main():
    spec = dict(
        fluentbit_bin=dict(type="path"),
    )

    module = AnsibleModule(argument_spec=spec, supports_check_mode=True)

    fluentbit_bin = find_fluentbit_binary(module)

    rc, stdout, stderr = module.run_command([fluentbit_bin, "--version"])
    if rc != 0:
        module.fail_json(msg="Failed to get fluent-bit version: %s" % stderr, rc=rc)

    match = re.search(r"Fluent Bit v([\d.]+)", stdout)
    version = match.group(1) if match else stdout.strip()

    module.exit_json(
        changed=False,
        version=version,
        binary_path=fluentbit_bin,
    )


if __name__ == "__main__":
    main()
