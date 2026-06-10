"""Unit tests for fluentd_gem_info module."""

from __future__ import absolute_import, division, print_function

__metaclass__ = type

from unittest.mock import MagicMock, patch

import pytest

MODULE_PATH = "ansible_collections.stevefulme1.fluentd.plugins.modules.fluentd_gem_info"


@patch(f"{MODULE_PATH}.AnsibleModule")
@patch(f"{MODULE_PATH}.find_gem_binary", return_value="/usr/sbin/fluent-gem")
@patch(f"{MODULE_PATH}.find_fluentd_binary", return_value="/usr/sbin/fluentd")
@patch(f"{MODULE_PATH}.get_fluentd_version", return_value="1.16.5")
@patch(
    f"{MODULE_PATH}.get_installed_plugins",
    return_value=[
        {"name": "fluent-plugin-elasticsearch", "version": "5.4.3"},
        {"name": "fluent-plugin-s3", "version": "1.7.2"},
    ],
)
class TestFluentdGemInfo:
    def test_list_all_plugins(self, mock_plugins, mock_ver, mock_fd, mock_gem, mock_ansible):
        module = MagicMock()
        module.params = {"config_path": None, "fluentd_bin": None, "name": None, "gem_bin": None}
        module.check_mode = False
        mock_ansible.return_value = module

        from ansible_collections.stevefulme1.fluentd.plugins.modules.fluentd_gem_info import main

        main()

        module.exit_json.assert_called_once()
        call_kwargs = module.exit_json.call_args.kwargs
        assert call_kwargs["changed"] is False
        assert len(call_kwargs["plugins"]) == 2
        assert call_kwargs["fluentd_version"] == "1.16.5"

    def test_filter_by_name(self, mock_plugins, mock_ver, mock_fd, mock_gem, mock_ansible):
        module = MagicMock()
        module.params = {"config_path": None, "fluentd_bin": None, "name": "fluent-plugin-s3", "gem_bin": None}
        module.check_mode = False
        mock_ansible.return_value = module

        from ansible_collections.stevefulme1.fluentd.plugins.modules.fluentd_gem_info import main

        main()

        call_kwargs = module.exit_json.call_args.kwargs
        assert len(call_kwargs["plugins"]) == 1
        assert call_kwargs["plugins"][0]["name"] == "fluent-plugin-s3"
