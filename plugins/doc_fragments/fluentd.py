# Copyright: (c) 2024, Steve Fulmer (@stevefulme1)
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type


class ModuleDocFragment:
    DOCUMENTATION = r"""
options:
  config_path:
    description:
      - Path to the fluentd configuration file.
      - When omitted, auto-detected from standard locations
        (C(/etc/fluent/fluentd.conf) or C(/etc/td-agent/td-agent.conf)).
    type: path
  fluentd_bin:
    description:
      - Path to the fluentd binary.
      - When omitted, auto-detected from standard locations.
    type: path
"""
