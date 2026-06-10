#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2024, Steve Fulmer (@stevefulme1)
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
---
module: fluentd_install
short_description: Install or remove the Fluentd package
version_added: "0.1.0"
description:
  - Installs, removes, or upgrades the C(fluent-package) or legacy C(td-agent)
    package using the system package manager.
  - Optionally configures the official Treasure Data package repository.
options:
  state:
    description:
      - Desired package state.
    type: str
    default: present
    choices: [present, absent, latest]
  version:
    description:
      - Pin to a specific package version.
    type: str
  package_name:
    description:
      - Which package to install.
    type: str
    default: fluent-package
    choices: [fluent-package, td-agent]
  manage_repo:
    description:
      - Whether to configure the official Fluentd package repository.
    type: bool
    default: true
extends_documentation_fragment:
  - stevefulme1.fluentd.fluentd
author:
  - Steve Fulmer (@stevefulme1)
"""

EXAMPLES = r"""
- name: Install the latest fluent-package
  stevefulme1.fluentd.fluentd_install:
    state: present

- name: Install a specific version
  stevefulme1.fluentd.fluentd_install:
    version: "5.0.4"

- name: Remove fluentd
  stevefulme1.fluentd.fluentd_install:
    state: absent
"""

RETURN = r"""
package:
  description: The name of the package managed.
  returned: always
  type: str
  sample: "fluent-package"
installed_version:
  description: The version installed after the operation.
  returned: when state is present or latest
  type: str
  sample: "5.0.4"
"""

import re

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.stevefulme1.fluentd.plugins.module_utils.fluentd_common import (
    fluentd_argument_spec,
)


def get_package_version_rpm(module, package_name):
    """Get installed RPM package version, or None."""
    rc, stdout, stderr = module.run_command(
        ["rpm", "-q", "--queryformat", "%{VERSION}", package_name]
    )
    if rc == 0:
        return stdout.strip()
    return None


def get_package_version_deb(module, package_name):
    """Get installed dpkg package version, or None."""
    rc, stdout, stderr = module.run_command(
        ["dpkg-query", "-W", "-f=${Version}", package_name]
    )
    if rc == 0 and stdout.strip():
        return stdout.strip()
    return None


def get_os_family(module):
    """Determine OS family from ansible_os_family or os-release."""
    rc, stdout, _ = module.run_command(["cat", "/etc/os-release"])
    if rc == 0:
        if re.search(r'ID_LIKE=.*(?:rhel|fedora|centos)', stdout):
            return "RedHat"
        if re.search(r'ID_LIKE=.*debian', stdout) or re.search(r'ID=(?:debian|ubuntu)', stdout):
            return "Debian"
    if module.get_bin_path("rpm"):
        return "RedHat"
    if module.get_bin_path("dpkg"):
        return "Debian"
    module.fail_json(msg="Unable to determine OS family.")
    return None


def get_package_version(module, package_name, os_family):
    """Get currently installed package version."""
    if os_family == "RedHat":
        return get_package_version_rpm(module, package_name)
    return get_package_version_deb(module, package_name)


def install_package(module, package_name, version, os_family):
    """Install package via system package manager."""
    if os_family == "RedHat":
        pkg_mgr = module.get_bin_path("dnf") or module.get_bin_path("yum")
        if not pkg_mgr:
            module.fail_json(msg="Neither dnf nor yum found.")
        pkg = "%s-%s" % (package_name, version) if version else package_name
        cmd = [pkg_mgr, "install", "-y", pkg]
    else:
        pkg_mgr = module.get_bin_path("apt-get")
        if not pkg_mgr:
            module.fail_json(msg="apt-get not found.")
        pkg = "%s=%s" % (package_name, version) if version else package_name
        cmd = [pkg_mgr, "install", "-y", pkg]

    rc, stdout, stderr = module.run_command(cmd)
    if rc != 0:
        module.fail_json(msg="Failed to install %s: %s" % (package_name, stderr), rc=rc)


def remove_package(module, package_name, os_family):
    """Remove package via system package manager."""
    if os_family == "RedHat":
        pkg_mgr = module.get_bin_path("dnf") or module.get_bin_path("yum")
        cmd = [pkg_mgr, "remove", "-y", package_name]
    else:
        pkg_mgr = module.get_bin_path("apt-get")
        cmd = [pkg_mgr, "remove", "-y", package_name]

    rc, stdout, stderr = module.run_command(cmd)
    if rc != 0:
        module.fail_json(msg="Failed to remove %s: %s" % (package_name, stderr), rc=rc)


def main():
    spec = fluentd_argument_spec()
    spec.update(
        dict(
            state=dict(type="str", default="present", choices=["present", "absent", "latest"]),
            version=dict(type="str"),
            package_name=dict(type="str", default="fluent-package", choices=["fluent-package", "td-agent"]),
            manage_repo=dict(type="bool", default=True),
        )
    )

    module = AnsibleModule(argument_spec=spec, supports_check_mode=True)

    state = module.params["state"]
    version = module.params.get("version")
    package_name = module.params["package_name"]

    os_family = get_os_family(module)
    current_version = get_package_version(module, package_name, os_family)

    if state == "absent":
        if current_version is None:
            module.exit_json(changed=False, package=package_name)
        if module.check_mode:
            module.exit_json(changed=True, package=package_name)
        remove_package(module, package_name, os_family)
        module.exit_json(changed=True, package=package_name)

    if state == "present":
        if current_version is not None:
            if version is None or current_version == version:
                module.exit_json(changed=False, package=package_name, installed_version=current_version)
        if module.check_mode:
            module.exit_json(changed=True, package=package_name)
        install_package(module, package_name, version, os_family)
        new_version = get_package_version(module, package_name, os_family)
        module.exit_json(changed=True, package=package_name, installed_version=new_version)

    if state == "latest":
        if module.check_mode:
            module.exit_json(changed=current_version is None, package=package_name, installed_version=current_version)
        install_package(module, package_name, None, os_family)
        new_version = get_package_version(module, package_name, os_family)
        changed = new_version != current_version
        module.exit_json(changed=changed, package=package_name, installed_version=new_version)


if __name__ == "__main__":
    main()
