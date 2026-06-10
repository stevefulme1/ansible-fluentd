"""Shared test fixtures for stevefulme1.fluentd collection."""

from __future__ import absolute_import, division, print_function

__metaclass__ = type
import os
import sys
from unittest.mock import MagicMock

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), os.pardir, os.pardir))


@pytest.fixture
def mock_module():
    """Create a mock AnsibleModule for fluentd modules."""
    module = MagicMock()
    module.params = {
        "config_path": "/etc/fluent/fluentd.conf",
        "fluentd_bin": "/usr/sbin/fluentd",
        "state": "present",
    }
    module.check_mode = False
    module.fail_json = MagicMock(side_effect=SystemExit(1))
    module.exit_json = MagicMock(side_effect=SystemExit(0))
    module.run_command = MagicMock(return_value=(0, "", ""))
    module.get_bin_path = MagicMock(return_value="/usr/sbin/fluentd")
    return module


@pytest.fixture
def mock_module_check_mode(mock_module):
    """Create a mock AnsibleModule in check mode."""
    mock_module.check_mode = True
    return mock_module
