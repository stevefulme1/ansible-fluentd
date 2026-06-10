"""Unit tests for fluentbit_config_validate module."""

from __future__ import absolute_import, division, print_function

__metaclass__ = type

from unittest.mock import MagicMock, patch

MODULE_PATH = (
    "ansible_collections.stevefulme1.fluentd.plugins.modules.fluentbit_config_validate"
)


@patch(f"{MODULE_PATH}.AnsibleModule")
@patch(f"{MODULE_PATH}.find_fluentbit_binary", return_value="/usr/sbin/fluent-bit")
class TestFluentbitConfigValidate:
    def test_valid_config(self, mock_find, mock_ansible):
        module = MagicMock()
        module.params = {
            "config_path": "/etc/fluent-bit/fluent-bit.conf",
            "fluentbit_bin": None,
        }
        module.run_command.return_value = (0, "configuration OK", "")
        mock_ansible.return_value = module

        from ansible_collections.stevefulme1.fluentd.plugins.modules.fluentbit_config_validate import (
            main,
        )

        main()

        call_kwargs = module.exit_json.call_args.kwargs
        assert call_kwargs["changed"] is False
        assert call_kwargs["valid"] is True

    def test_invalid_config(self, mock_find, mock_ansible):
        module = MagicMock()
        module.params = {
            "config_path": "/etc/fluent-bit/bad.conf",
            "fluentbit_bin": None,
        }
        module.run_command.return_value = (1, "", "error in config\ninvalid key")
        mock_ansible.return_value = module

        from ansible_collections.stevefulme1.fluentd.plugins.modules.fluentbit_config_validate import (
            main,
        )

        main()

        call_kwargs = module.exit_json.call_args.kwargs
        assert call_kwargs["valid"] is False
        assert len(call_kwargs["errors"]) == 2
