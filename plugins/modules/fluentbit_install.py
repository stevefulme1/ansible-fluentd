#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2024, Steve Fulmer (@stevefulme1)
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
---
module: fluentbit_install
short_description: Install or remove the Fluent Bit package
version_added: "0.1.0"
description:
  - Installs, removes, or upgrades the C(fluent-bit) package using the
    system package manager.
  - Optionally configures the official Fluent Bit package repository.
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
  manage_repo:
    description:
      - Whether to configure the official Fluent Bit package repository.
    type: bool
    default: true
author:
  - Steve Fulmer (@stevefulme1)
"""

EXAMPLES = r"""
- name: Install fluent-bit
  stevefulme1.fluentd.fluentbit_install:
    state: present

- name: Remove fluent-bit
  stevefulme1.fluentd.fluentbit_install:
    state: absent
"""

RETURN = r"""
package:
  description: The name of the package managed.
  returned: always
  type: str
  sample: "fluent-bit"
installed_version:
  description: The version installed after the operation.
  returned: when state is present or latest
  type: str
  sample: "3.0.4"
"""

import re

from ansible.module_utils.basic import AnsibleModule


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
    """Determine OS family."""
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


def get_package_version(module, os_family):
    """Get currently installed fluent-bit version."""
    if os_family == "RedHat":
        return get_package_version_rpm(module, "fluent-bit")
    return get_package_version_deb(module, "fluent-bit")


def install_package(module, version, os_family):
    """Install fluent-bit via system package manager."""
    if os_family == "RedHat":
        pkg_mgr = module.get_bin_path("dnf") or module.get_bin_path("yum")
        if not pkg_mgr:
            module.fail_json(msg="Neither dnf nor yum found.")
        pkg = "fluent-bit-%s" % version if version else "fluent-bit"
        cmd = [pkg_mgr, "install", "-y", pkg]
    else:
        pkg_mgr = module.get_bin_path("apt-get")
        if not pkg_mgr:
            module.fail_json(msg="apt-get not found.")
        pkg = "fluent-bit=%s" % version if version else "fluent-bit"
        cmd = [pkg_mgr, "install", "-y", pkg]

    rc, stdout, stderr = module.run_command(cmd)
    if rc != 0:
        module.fail_json(msg="Failed to install fluent-bit: %s" % stderr, rc=rc)


def remove_package(module, os_family):
    """Remove fluent-bit via system package manager."""
    if os_family == "RedHat":
        pkg_mgr = module.get_bin_path("dnf") or module.get_bin_path("yum")
        cmd = [pkg_mgr, "remove", "-y", "fluent-bit"]
    else:
        pkg_mgr = module.get_bin_path("apt-get")
        cmd = [pkg_mgr, "remove", "-y", "fluent-bit"]

    rc, stdout, stderr = module.run_command(cmd)
    if rc != 0:
        module.fail_json(msg="Failed to remove fluent-bit: %s" % stderr, rc=rc)


def main():
    spec = dict(
        state=dict(type="str", default="present", choices=["present", "absent", "latest"]),
        version=dict(type="str"),
        manage_repo=dict(type="bool", default=True),
    )

    module = AnsibleModule(argument_spec=spec, supports_check_mode=True)

    state = module.params["state"]
    version = module.params.get("version")

    os_family = get_os_family(module)
    current_version = get_package_version(module, os_family)

    if state == "absent":
        if current_version is None:
            module.exit_json(changed=False, package="fluent-bit")
        if module.check_mode:
            module.exit_json(changed=True, package="fluent-bit")
        remove_package(module, os_family)
        module.exit_json(changed=True, package="fluent-bit")

    if state == "present":
        if current_version is not None:
            if version is None or current_version == version:
                module.exit_json(changed=False, package="fluent-bit", installed_version=current_version)
        if module.check_mode:
            module.exit_json(changed=True, package="fluent-bit")
        install_package(module, version, os_family)
        new_version = get_package_version(module, os_family)
        module.exit_json(changed=True, package="fluent-bit", installed_version=new_version)

    if state == "latest":
        if module.check_mode:
            module.exit_json(changed=current_version is None, package="fluent-bit", installed_version=current_version)
        install_package(module, None, os_family)
        new_version = get_package_version(module, os_family)
        changed = new_version != current_version
        module.exit_json(changed=changed, package="fluent-bit", installed_version=new_version)


if __name__ == "__main__":
    main()
