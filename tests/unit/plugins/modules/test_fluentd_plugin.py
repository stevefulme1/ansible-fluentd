"""Unit tests for fluentd_plugin module."""

from __future__ import absolute_import, division, print_function

__metaclass__ = type

from unittest.mock import MagicMock, patch

import pytest

MODULE_PATH = "ansible_collections.stevefulme1.fluentd.plugins.modules.fluentd_plugin"

PLUGIN_LIST_OUTPUT = "fluent-plugin-elasticsearch (5.4.3)\nfluent-plugin-s3 (1.7.2)\n"
EMPTY_LIST_OUTPUT = ""


@patch(f"{MODULE_PATH}.AnsibleModule")
@patch(f"{MODULE_PATH}.find_gem_binary", return_value="/usr/sbin/fluent-gem")
class TestFluentdPlugin:
    def _make_module(self, mock_ansible, **kwargs):
        module = MagicMock()
        module.params = {
            "config_path": None,
            "fluentd_bin": None,
            "name": "fluent-plugin-elasticsearch",
            "state": "present",
            "version": None,
            "gem_bin": None,
        }
        module.params.update(kwargs)
        module.check_mode = False
        module.run_command.return_value = (0, "", "")
        module.exit_json.side_effect = SystemExit(0)
        module.fail_json.side_effect = SystemExit(1)
        mock_ansible.return_value = module
        return module

    def test_present_already_installed(self, mock_gem, mock_ansible):
        module = self._make_module(mock_ansible)
        module.run_command.return_value = (0, PLUGIN_LIST_OUTPUT, "")

        from ansible_collections.stevefulme1.fluentd.plugins.modules.fluentd_plugin import main

        with pytest.raises(SystemExit):
            main()

        call_kwargs = module.exit_json.call_args.kwargs
        assert call_kwargs["changed"] is False
        assert call_kwargs["version"] == "5.4.3"

    def test_present_not_installed(self, mock_gem, mock_ansible):
        module = self._make_module(mock_ansible)
        module.run_command.side_effect = [
            (0, EMPTY_LIST_OUTPUT, ""),  # gem list --local (empty)
            (0, "installed", ""),  # gem install
            (0, PLUGIN_LIST_OUTPUT, ""),  # gem list --local (after install)
        ]

        from ansible_collections.stevefulme1.fluentd.plugins.modules.fluentd_plugin import main

        with pytest.raises(SystemExit):
            main()

        call_kwargs = module.exit_json.call_args.kwargs
        assert call_kwargs["changed"] is True

    def test_absent_installed(self, mock_gem, mock_ansible):
        module = self._make_module(mock_ansible, state="absent")
        module.run_command.side_effect = [
            (0, PLUGIN_LIST_OUTPUT, ""),  # gem list --local
            (0, "removed", ""),  # gem uninstall
        ]

        from ansible_collections.stevefulme1.fluentd.plugins.modules.fluentd_plugin import main

        with pytest.raises(SystemExit):
            main()

        call_kwargs = module.exit_json.call_args.kwargs
        assert call_kwargs["changed"] is True

    def test_absent_not_installed(self, mock_gem, mock_ansible):
        module = self._make_module(mock_ansible, state="absent")
        module.run_command.return_value = (0, EMPTY_LIST_OUTPUT, "")

        from ansible_collections.stevefulme1.fluentd.plugins.modules.fluentd_plugin import main

        with pytest.raises(SystemExit):
            main()

        call_kwargs = module.exit_json.call_args.kwargs
        assert call_kwargs["changed"] is False

    def test_check_mode_present(self, mock_gem, mock_ansible):
        module = self._make_module(mock_ansible)
        module.check_mode = True
        module.run_command.return_value = (0, EMPTY_LIST_OUTPUT, "")

        from ansible_collections.stevefulme1.fluentd.plugins.modules.fluentd_plugin import main

        with pytest.raises(SystemExit):
            main()

        call_kwargs = module.exit_json.call_args.kwargs
        assert call_kwargs["changed"] is True
