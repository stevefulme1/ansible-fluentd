"""Unit tests for fluentbit_install module."""

from __future__ import absolute_import, division, print_function

__metaclass__ = type

from unittest.mock import MagicMock, patch

import pytest

MODULE_PATH = "ansible_collections.stevefulme1.fluentd.plugins.modules.fluentbit_install"


@patch(f"{MODULE_PATH}.AnsibleModule")
@patch(f"{MODULE_PATH}.get_os_family", return_value="RedHat")
class TestFluentbitInstall:
    def _make_module(self, mock_ansible, **kwargs):
        module = MagicMock()
        module.params = {
            "state": "present",
            "version": None,
            "manage_repo": True,
        }
        module.params.update(kwargs)
        module.check_mode = False
        module.run_command.return_value = (0, "", "")
        module.get_bin_path.return_value = "/usr/bin/dnf"
        module.exit_json.side_effect = SystemExit(0)
        module.fail_json.side_effect = SystemExit(1)
        mock_ansible.return_value = module
        return module

    def test_present_already_installed(self, mock_os, mock_ansible):
        module = self._make_module(mock_ansible)
        module.run_command.return_value = (0, "3.0.4", "")

        from ansible_collections.stevefulme1.fluentd.plugins.modules.fluentbit_install import main

        with pytest.raises(SystemExit):
            main()

        call_kwargs = module.exit_json.call_args.kwargs
        assert call_kwargs["changed"] is False

    def test_present_not_installed(self, mock_os, mock_ansible):
        module = self._make_module(mock_ansible)
        module.run_command.side_effect = [
            (1, "", "not installed"),
            (0, "", ""),
            (0, "3.0.4", ""),
        ]

        from ansible_collections.stevefulme1.fluentd.plugins.modules.fluentbit_install import main

        with pytest.raises(SystemExit):
            main()

        call_kwargs = module.exit_json.call_args.kwargs
        assert call_kwargs["changed"] is True

    def test_absent_installed(self, mock_os, mock_ansible):
        module = self._make_module(mock_ansible, state="absent")
        module.run_command.side_effect = [
            (0, "3.0.4", ""),
            (0, "", ""),
        ]

        from ansible_collections.stevefulme1.fluentd.plugins.modules.fluentbit_install import main

        with pytest.raises(SystemExit):
            main()

        call_kwargs = module.exit_json.call_args.kwargs
        assert call_kwargs["changed"] is True

    def test_absent_not_installed(self, mock_os, mock_ansible):
        module = self._make_module(mock_ansible, state="absent")
        module.run_command.return_value = (1, "", "not installed")

        from ansible_collections.stevefulme1.fluentd.plugins.modules.fluentbit_install import main

        with pytest.raises(SystemExit):
            main()

        call_kwargs = module.exit_json.call_args.kwargs
        assert call_kwargs["changed"] is False
