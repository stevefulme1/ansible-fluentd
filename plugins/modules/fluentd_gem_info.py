#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2024, Steve Fulmer (@stevefulme1)
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
---
module: fluentd_gem_info
short_description: List installed Fluentd plugins
version_added: "0.1.0"
description:
  - Retrieves a list of gems installed via C(fluent-gem).
  - Optionally filters to a single plugin by name.
  - This is an info module and never reports C(changed).
options:
  name:
    description:
      - Filter results to a specific plugin gem name.
    type: str
  gem_bin:
    description:
      - Path to the C(fluent-gem) binary.
      - Auto-detected when omitted.
    type: path
extends_documentation_fragment:
  - stevefulme1.fluentd.fluentd
author:
  - Steve Fulmer (@stevefulme1)
"""

EXAMPLES = r"""
- name: List all installed fluentd plugins
  stevefulme1.fluentd.fluentd_gem_info:
  register: result

- name: Check if a specific plugin is installed
  stevefulme1.fluentd.fluentd_gem_info:
    name: fluent-plugin-elasticsearch
  register: result
"""

RETURN = r"""
plugins:
  description: List of installed Fluentd plugins.
  returned: always
  type: list
  elements: dict
  contains:
    name:
      description: Plugin gem name.
      type: str
      sample: "fluent-plugin-elasticsearch"
    version:
      description: Installed version.
      type: str
      sample: "5.4.3"
fluentd_version:
  description: The installed Fluentd version.
  returned: always
  type: str
  sample: "1.16.5"
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.stevefulme1.fluentd.plugins.module_utils.fluentd_common import (
    find_fluentd_binary,
    find_gem_binary,
    fluentd_argument_spec,
    get_fluentd_version,
    get_installed_plugins,
)


def main():
    spec = fluentd_argument_spec()
    spec.update(
        dict(
            name=dict(type="str"),
            gem_bin=dict(type="path"),
        )
    )

    module = AnsibleModule(argument_spec=spec, supports_check_mode=True)

    gem_bin = module.params.get("gem_bin") or find_gem_binary(module)
    fluentd_bin = find_fluentd_binary(module)

    plugins = get_installed_plugins(module, gem_bin)
    version = get_fluentd_version(module, fluentd_bin)

    if module.params.get("name"):
        plugins = [p for p in plugins if p["name"] == module.params["name"]]

    module.exit_json(changed=False, plugins=plugins, fluentd_version=version)


if __name__ == "__main__":
    main()
