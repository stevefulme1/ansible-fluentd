# Copyright: (c) 2024, Steve Fulmer (@stevefulme1)
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import os
import re


def fluentd_argument_spec():
    """Common argument spec shared by all fluentd modules."""
    return dict(
        config_path=dict(type="path", default=None),
        fluentd_bin=dict(type="path", default=None),
    )


def find_fluentd_binary(module):
    """Locate the fluentd binary.

    Search order:
    1. module.params['fluentd_bin'] if provided
    2. /opt/fluent/bin/fluentd (fluent-package v5+)
    3. /usr/sbin/fluentd (fluent-package)
    4. /usr/sbin/td-agent (legacy td-agent)
    5. module.get_bin_path('fluentd')
    """
    if module.params.get("fluentd_bin"):
        return module.params["fluentd_bin"]

    candidates = [
        "/opt/fluent/bin/fluentd",
        "/usr/sbin/fluentd",
        "/usr/sbin/td-agent",
    ]
    for path in candidates:
        if os.path.isfile(path) and os.access(path, os.X_OK):
            return path

    found = module.get_bin_path("fluentd")
    if found:
        return found

    module.fail_json(
        msg="Unable to find fluentd binary. Install fluent-package or set fluentd_bin."
    )
    return None


def find_gem_binary(module):
    """Locate the fluent-gem binary."""
    candidates = [
        "/opt/fluent/bin/fluent-gem",
        "/usr/sbin/fluent-gem",
        "/usr/sbin/td-agent-gem",
    ]
    for path in candidates:
        if os.path.isfile(path) and os.access(path, os.X_OK):
            return path

    found = module.get_bin_path("fluent-gem")
    if found:
        return found

    module.fail_json(
        msg="Unable to find fluent-gem binary. Install fluent-package or set gem_bin."
    )
    return None


def find_fluentbit_binary(module):
    """Locate the fluent-bit binary."""
    if module.params.get("fluentbit_bin"):
        return module.params["fluentbit_bin"]

    candidates = [
        "/opt/fluent-bit/bin/fluent-bit",
        "/usr/sbin/fluent-bit",
        "/usr/bin/fluent-bit",
    ]
    for path in candidates:
        if os.path.isfile(path) and os.access(path, os.X_OK):
            return path

    found = module.get_bin_path("fluent-bit")
    if found:
        return found

    module.fail_json(
        msg="Unable to find fluent-bit binary. Install fluent-bit or set fluentbit_bin."
    )
    return None


def get_default_config_path():
    """Return the default fluentd config path."""
    candidates = [
        "/etc/fluent/fluentd.conf",
        "/etc/td-agent/td-agent.conf",
    ]
    for path in candidates:
        if os.path.isfile(path):
            return path
    return "/etc/fluent/fluentd.conf"


def get_installed_plugins(module, gem_bin):
    """Run fluent-gem list and parse into list of dicts."""
    rc, stdout, stderr = module.run_command([gem_bin, "list", "--local"])
    if rc != 0:
        module.fail_json(msg="Failed to list plugins: %s" % stderr, rc=rc)

    plugins = []
    for line in stdout.strip().splitlines():
        match = re.match(r"^(\S+)\s+\((.+)\)$", line)
        if match:
            name = match.group(1)
            versions = [v.strip() for v in match.group(2).split(",")]
            plugins.append(dict(name=name, version=versions[0]))
    return plugins


def get_fluentd_version(module, fluentd_bin):
    """Run fluentd --version and return the version string."""
    rc, stdout, stderr = module.run_command([fluentd_bin, "--version"])
    if rc != 0:
        module.fail_json(msg="Failed to get fluentd version: %s" % stderr, rc=rc)

    match = re.search(r"fluentd\s+([\d.]+)", stdout)
    if match:
        return match.group(1)

    return stdout.strip()
