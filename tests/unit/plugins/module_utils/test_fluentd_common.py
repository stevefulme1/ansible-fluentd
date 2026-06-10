"""Unit tests for fluentd_common module_utils."""

from __future__ import absolute_import, division, print_function

__metaclass__ = type

from unittest.mock import MagicMock, patch

import pytest

from ansible_collections.stevefulme1.fluentd.plugins.module_utils.fluentd_common import (
    find_fluentd_binary,
    find_fluentbit_binary,
    find_gem_binary,
    get_default_config_path,
    get_fluentd_version,
    get_installed_plugins,
)


class TestFindFluentdBinary:
    def test_explicit_param(self, mock_module):
        mock_module.params = {"fluentd_bin": "/custom/fluentd"}
        assert find_fluentd_binary(mock_module) == "/custom/fluentd"

    @patch("os.path.isfile", return_value=True)
    @patch("os.access", return_value=True)
    def test_standard_path(self, mock_access, mock_isfile, mock_module):
        mock_module.params = {"fluentd_bin": None}
        assert find_fluentd_binary(mock_module) == "/opt/fluent/bin/fluentd"

    @patch("os.path.isfile", return_value=False)
    def test_get_bin_path_fallback(self, mock_isfile, mock_module):
        mock_module.params = {"fluentd_bin": None}
        mock_module.get_bin_path.return_value = "/usr/local/bin/fluentd"
        assert find_fluentd_binary(mock_module) == "/usr/local/bin/fluentd"

    @patch("os.path.isfile", return_value=False)
    def test_not_found(self, mock_isfile, mock_module):
        mock_module.params = {"fluentd_bin": None}
        mock_module.get_bin_path.return_value = None
        with pytest.raises(SystemExit):
            find_fluentd_binary(mock_module)
        mock_module.fail_json.assert_called_once()


class TestFindGemBinary:
    @patch("os.path.isfile", return_value=True)
    @patch("os.access", return_value=True)
    def test_standard_path(self, mock_access, mock_isfile, mock_module):
        assert find_gem_binary(mock_module) == "/opt/fluent/bin/fluent-gem"

    @patch("os.path.isfile", return_value=False)
    def test_not_found(self, mock_isfile, mock_module):
        mock_module.get_bin_path.return_value = None
        with pytest.raises(SystemExit):
            find_gem_binary(mock_module)


class TestFindFluentbitBinary:
    def test_explicit_param(self, mock_module):
        mock_module.params = {"fluentbit_bin": "/custom/fluent-bit"}
        assert find_fluentbit_binary(mock_module) == "/custom/fluent-bit"

    @patch("os.path.isfile", return_value=False)
    def test_not_found(self, mock_isfile, mock_module):
        mock_module.params = {"fluentbit_bin": None}
        mock_module.get_bin_path.return_value = None
        with pytest.raises(SystemExit):
            find_fluentbit_binary(mock_module)


class TestGetInstalledPlugins:
    def test_parses_gem_list(self, mock_module):
        mock_module.run_command.return_value = (
            0,
            "fluent-plugin-elasticsearch (5.4.3)\nfluent-plugin-s3 (1.7.2)\n",
            "",
        )
        plugins = get_installed_plugins(mock_module, "/usr/sbin/fluent-gem")
        assert len(plugins) == 2
        assert plugins[0] == {"name": "fluent-plugin-elasticsearch", "version": "5.4.3"}

    def test_empty_list(self, mock_module):
        mock_module.run_command.return_value = (0, "", "")
        plugins = get_installed_plugins(mock_module, "/usr/sbin/fluent-gem")
        assert plugins == []

    def test_failure(self, mock_module):
        mock_module.run_command.return_value = (1, "", "error")
        with pytest.raises(SystemExit):
            get_installed_plugins(mock_module, "/usr/sbin/fluent-gem")


class TestGetFluentdVersion:
    def test_parses_version(self, mock_module):
        mock_module.run_command.return_value = (0, "fluentd 1.16.5", "")
        assert get_fluentd_version(mock_module, "/usr/sbin/fluentd") == "1.16.5"


class TestGetDefaultConfigPath:
    @patch("os.path.isfile")
    def test_fluent_package(self, mock_isfile):
        mock_isfile.side_effect = lambda p: p == "/etc/fluent/fluentd.conf"
        assert get_default_config_path() == "/etc/fluent/fluentd.conf"

    @patch("os.path.isfile", return_value=False)
    def test_fallback(self, mock_isfile):
        assert get_default_config_path() == "/etc/fluent/fluentd.conf"
