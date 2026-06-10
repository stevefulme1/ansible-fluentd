# Changelog

All notable changes to this collection will be documented in this file.

## [0.1.0] - Unreleased

### Added

- Initial collection scaffolding.
- Modules: `fluentd_install`, `fluentd_plugin`, `fluentd_config_validate`, `fluentd_gem_info`, `fluentbit_install`, `fluentbit_config_validate`.
- Roles: `install`, `forwarder`, `aggregator`, `fluentbit`.
- Filter plugin: `fluentd_parse_config`.
- EDA event source plugins: `fluentd_monitor`, `fluentd_webhook`.
- EDA rulebooks: `fluentd_alert_remediation`, `fluentd_webhook_handler`.
- Indirect node counting queries in `extensions/audit/event_query.yml`.
