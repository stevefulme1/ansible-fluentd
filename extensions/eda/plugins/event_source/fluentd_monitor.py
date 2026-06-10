# -*- coding: utf-8 -*-

# Copyright: (c) 2024, Steve Fulmer (@stevefulme1)
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
---
name: fluentd_monitor
short_description: Watch Fluentd monitor API for plugin issues
description:
  - Polls the Fluentd HTTP monitor agent API for plugins with high retry
    counts, large buffer queues, or error states.
  - Each anomaly is emitted as an event for EDA rule matching.
options:
  api_url:
    description: Fluentd monitor agent URL (e.g. C(http://localhost:24220)).
    type: str
    required: true
  interval:
    description: Polling interval in seconds.
    type: int
    default: 30
  validate_certs:
    description: Whether to validate SSL certificates.
    type: bool
    default: true
  retry_threshold:
    description: Emit an event when a plugin retry count exceeds this value.
    type: int
    default: 3
  buffer_threshold:
    description: Emit an event when buffer total_queued_size exceeds this value.
    type: int
    default: 100
"""

EXAMPLES = r"""
- name: Monitor fluentd for plugin issues
  stevefulme1.fluentd.fluentd_monitor:
    api_url: "http://localhost:24220"
    interval: 30
    retry_threshold: 5
    buffer_threshold: 200
"""

import asyncio
import logging
from datetime import datetime, timezone

try:
    import aiohttp
except ImportError:
    aiohttp = None

logger = logging.getLogger("fluentd_monitor")


async def main(queue: asyncio.Queue, args: dict) -> None:
    """Poll fluentd monitor API and emit events on anomalies."""
    api_url = args["api_url"].rstrip("/")
    interval = int(args.get("interval", 30))
    validate_certs = args.get("validate_certs", True)
    retry_threshold = int(args.get("retry_threshold", 3))
    buffer_threshold = int(args.get("buffer_threshold", 100))

    ssl = None if validate_certs else False
    url = "%s/api/plugins.json" % api_url

    async with aiohttp.ClientSession() as session:
        while True:
            try:
                async with session.get(url, ssl=ssl) as resp:
                    if resp.status != 200:
                        logger.warning("Monitor API returned %d", resp.status)
                        await asyncio.sleep(interval)
                        continue

                    data = await resp.json()
                    timestamp = datetime.now(timezone.utc).isoformat()

                    for plugin in data.get("plugins", []):
                        plugin_id = plugin.get("plugin_id", "unknown")
                        plugin_type = plugin.get("type", "unknown")

                        retry_count = plugin.get("retry_count", 0)
                        if retry_count and int(retry_count) > retry_threshold:
                            await queue.put(
                                {
                                    "fluentd_monitor": {
                                        "event_type": "retry_exceeded",
                                        "plugin_id": plugin_id,
                                        "plugin_type": plugin_type,
                                        "retry_count": retry_count,
                                        "threshold": retry_threshold,
                                        "timestamp": timestamp,
                                    }
                                }
                            )

                        buffer_info = plugin.get("buffer", {})
                        queued = buffer_info.get("total_queued_size", 0)
                        if queued and int(queued) > buffer_threshold:
                            await queue.put(
                                {
                                    "fluentd_monitor": {
                                        "event_type": "buffer_overflow",
                                        "plugin_id": plugin_id,
                                        "plugin_type": plugin_type,
                                        "total_queued_size": queued,
                                        "threshold": buffer_threshold,
                                        "timestamp": timestamp,
                                    }
                                }
                            )

                        if plugin.get("output_plugin") and plugin.get("retry"):
                            retry_info = plugin.get("retry", {})
                            if retry_info.get("steps", 0) > 0:
                                await queue.put(
                                    {
                                        "fluentd_monitor": {
                                            "event_type": "plugin_retry",
                                            "plugin_id": plugin_id,
                                            "plugin_type": plugin_type,
                                            "retry_steps": retry_info.get("steps"),
                                            "next_retry": retry_info.get("next_time"),
                                            "timestamp": timestamp,
                                        }
                                    }
                                )

            except Exception as exc:
                logger.error("Failed to poll fluentd monitor API: %s", exc)

            await asyncio.sleep(interval)


if __name__ == "__main__":
    asyncio.run(main(asyncio.Queue(), {"api_url": "http://localhost:24220"}))
