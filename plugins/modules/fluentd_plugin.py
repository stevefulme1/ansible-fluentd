#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2024, Steve Fulmer (@stevefulme1)
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
---
module: fluentd_plugin
short_description: Manage Fluentd gem plugins
version_added: "0.1.0"
description:
  - Installs, removes, or updates Fluentd plugins via C(fluent-gem).
options:
  name:
    description:
      - The gem name of the plugin to manage.
    type: str
    required: true
  state:
    description:
      - Desired state of the plugin.
    type: str
    default: present
    choices: [present, absent, latest]
  version:
    description:
      - Pin to a specific gem version when C(state=present).
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
- name: Install the elasticsearch plugin
  stevefulme1.fluentd.fluentd_plugin:
    name: fluent-plugin-elasticsearch
    state: present

- name: Install a specific version
  stevefulme1.fluentd.fluentd_plugin:
    name: fluent-plugin-elasticsearch
    version: "5.4.3"

- name: Remove a plugin
  stevefulme1.fluentd.fluentd_plugin:
    name: fluent-plugin-elasticsearch
    state: absent
"""

RETURN = r"""
name:
  description: The plugin gem name.
  returned: always
  type: str
  sample: "fluent-plugin-elasticsearch"
version:
  description: The installed version after the operation.
  returned: when state is present or latest
  type: str
  sample: "5.4.3"
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.stevefulme1.fluentd.plugins.module_utils.fluentd_common import (
    find_gem_binary,
    fluentd_argument_spec,
    get_installed_plugins,
)


def get_plugin_state(module, gem_bin, name):
    """Return the installed version of a gem, or None."""
    plugins = get_installed_plugins(module, gem_bin)
    for p in plugins:
        if p["name"] == name:
            return p["version"]
    return None


def main():
    spec = fluentd_argument_spec()
    spec.update(
        dict(
            name=dict(type="str", required=True),
            state=dict(type="str", default="present", choices=["present", "absent", "latest"]),
            version=dict(type="str"),
            gem_bin=dict(type="path"),
        )
    )

    module = AnsibleModule(argument_spec=spec, supports_check_mode=True)

    gem_bin = module.params.get("gem_bin") or find_gem_binary(module)
    name = module.params["name"]
    state = module.params["state"]
    version = module.params.get("version")

    current_version = get_plugin_state(module, gem_bin, name)

    if state == "absent":
        if current_version is None:
            module.exit_json(changed=False, name=name)
        if module.check_mode:
            module.exit_json(changed=True, name=name)
        rc, stdout, stderr = module.run_command(
            [gem_bin, "uninstall", name, "-x", "-a"]
        )
        if rc != 0:
            module.fail_json(msg="Failed to uninstall %s: %s" % (name, stderr), rc=rc)
        module.exit_json(changed=True, name=name)

    if state == "present":
        if current_version is not None:
            if version is None or current_version == version:
                module.exit_json(changed=False, name=name, version=current_version)
        if module.check_mode:
            module.exit_json(changed=True, name=name)
        cmd = [gem_bin, "install", name]
        if version:
            cmd.extend(["--version", version])
        rc, stdout, stderr = module.run_command(cmd)
        if rc != 0:
            module.fail_json(msg="Failed to install %s: %s" % (name, stderr), rc=rc)
        installed = get_plugin_state(module, gem_bin, name)
        module.exit_json(changed=True, name=name, version=installed)

    if state == "latest":
        cmd = [gem_bin, "install", name]
        if module.check_mode:
            changed = current_version is None
            module.exit_json(changed=changed, name=name, version=current_version)
        rc, stdout, stderr = module.run_command(cmd)
        if rc != 0:
            module.fail_json(msg="Failed to install %s: %s" % (name, stderr), rc=rc)
        new_version = get_plugin_state(module, gem_bin, name)
        changed = new_version != current_version
        module.exit_json(changed=changed, name=name, version=new_version)


if __name__ == "__main__":
    main()
