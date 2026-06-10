#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2024, Steve Fulmer (@stevefulme1)
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
---
module: fluentd_config_validate
short_description: Validate a Fluentd configuration file
version_added: "0.1.0"
description:
  - Runs C(fluentd --dry-run) against a configuration file and reports
    whether the configuration is valid.
  - This module never reports C(changed).
options:
  config_path:
    description:
      - Path to the Fluentd configuration file to validate.
    type: path
    required: true
  fluentd_bin:
    description:
      - Path to the fluentd binary.
      - Auto-detected when omitted.
    type: path
author:
  - Steve Fulmer (@stevefulme1)
"""

EXAMPLES = r"""
- name: Validate the default fluentd config
  stevefulme1.fluentd.fluentd_config_validate:
    config_path: /etc/fluent/fluentd.conf
  register: result

- name: Fail if config is invalid
  stevefulme1.fluentd.fluentd_config_validate:
    config_path: /etc/fluent/fluentd.conf
  register: result
  failed_when: not result.valid
"""

RETURN = r"""
valid:
  description: Whether the configuration passed validation.
  returned: always
  type: bool
  sample: true
stdout:
  description: Standard output from the validation command.
  returned: always
  type: str
stderr:
  description: Standard error from the validation command.
  returned: always
  type: str
errors:
  description: List of parsed error messages from validation.
  returned: when valid is false
  type: list
  elements: str
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.stevefulme1.fluentd.plugins.module_utils.fluentd_common import (
    find_fluentd_binary,
)


def main():
    spec = dict(
        config_path=dict(type="path", required=True),
        fluentd_bin=dict(type="path"),
    )

    module = AnsibleModule(argument_spec=spec, supports_check_mode=True)

    fluentd_bin = find_fluentd_binary(module)
    config_path = module.params["config_path"]

    rc, stdout, stderr = module.run_command(
        [fluentd_bin, "--dry-run", "-c", config_path]
    )

    valid = rc == 0
    result = dict(
        changed=False,
        valid=valid,
        stdout=stdout,
        stderr=stderr,
    )

    if not valid:
        errors = [line for line in stderr.splitlines() if line.strip()]
        result["errors"] = errors

    module.exit_json(**result)


if __name__ == "__main__":
    main()
