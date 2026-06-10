#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2024, Steve Fulmer (@stevefulme1)
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
---
module: fluentd_info
short_description: Gather Fluentd installation information
version_added: "0.1.0"
description:
  - Returns information about the installed Fluentd instance including
    version, binary path, configuration path, and installed plugins.
  - This is an info module and never reports C(changed).
extends_documentation_fragment:
  - stevefulme1.fluentd.fluentd
author:
  - Steve Fulmer (@stevefulme1)
"""

EXAMPLES = r"""
- name: Get fluentd installation info
  stevefulme1.fluentd.fluentd_info:
  register: result

- name: Display fluentd version
  ansible.builtin.debug:
    msg: "Fluentd version {{ result.version }}"
"""

RETURN = r"""
version:
  description: Installed Fluentd version.
  returned: always
  type: str
  sample: "1.16.5"
binary_path:
  description: Path to the fluentd binary.
  returned: always
  type: str
  sample: "/usr/sbin/fluentd"
config_path:
  description: Default configuration file path.
  returned: always
  type: str
  sample: "/etc/fluent/fluentd.conf"
gem_binary_path:
  description: Path to the fluent-gem binary.
  returned: always
  type: str
  sample: "/usr/sbin/fluent-gem"
plugins:
  description: List of installed plugins.
  returned: always
  type: list
  elements: dict
  contains:
    name:
      description: Plugin gem name.
      type: str
    version:
      description: Installed version.
      type: str
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.stevefulme1.fluentd.plugins.module_utils.fluentd_common import (
    find_fluentd_binary,
    find_gem_binary,
    fluentd_argument_spec,
    get_default_config_path,
    get_fluentd_version,
    get_installed_plugins,
)


def main():
    spec = fluentd_argument_spec()

    module = AnsibleModule(argument_spec=spec, supports_check_mode=True)

    fluentd_bin = find_fluentd_binary(module)
    gem_bin = find_gem_binary(module)
    version = get_fluentd_version(module, fluentd_bin)
    config_path = module.params.get("config_path") or get_default_config_path()
    plugins = get_installed_plugins(module, gem_bin)

    module.exit_json(
        changed=False,
        version=version,
        binary_path=fluentd_bin,
        config_path=config_path,
        gem_binary_path=gem_bin,
        plugins=plugins,
    )


if __name__ == "__main__":
    main()
