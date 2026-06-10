# -*- coding: utf-8 -*-

# Copyright: (c) 2024, Steve Fulmer (@stevefulme1)
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
---
name: fluentd_webhook
short_description: Receive events from Fluentd out_http plugin
description:
  - Starts an HTTP server that receives JSON payloads from Fluentd's
    C(out_http) output plugin.
  - Each received payload is emitted as an EDA event.
options:
  host:
    description: Address to bind the webhook listener.
    type: str
    default: "127.0.0.1"
  port:
    description: Port to listen on.
    type: int
    default: 5000
  token:
    description:
      - Optional bearer token for authentication.
      - When set, requests must include an C(Authorization: Bearer <token>) header.
    type: str
    secret: true
"""

EXAMPLES = r"""
- name: Listen for fluentd HTTP output events
  stevefulme1.fluentd.fluentd_webhook:
    host: "0.0.0.0"
    port: 5000

- name: Listen with authentication
  stevefulme1.fluentd.fluentd_webhook:
    host: "0.0.0.0"
    port: 5000
    token: "{{ webhook_secret }}"
"""

import asyncio
import logging

try:
    from aiohttp import web
except ImportError:
    web = None

logger = logging.getLogger("fluentd_webhook")


async def main(queue: asyncio.Queue, args: dict) -> None:
    """Start webhook server to receive fluentd out_http payloads."""
    host = str(args.get("host", "127.0.0.1"))
    port = int(args.get("port", 5000))
    token = args.get("token")

    app = web.Application()

    async def _handle_webhook(request: web.Request) -> web.Response:
        if token:
            auth_header = request.headers.get("Authorization", "")
            if auth_header != "Bearer %s" % token:
                return web.Response(status=401, text="Unauthorized")

        try:
            payload = await request.json()
            await queue.put({"fluentd_webhook": payload})
            return web.Response(status=200, text="OK")
        except Exception as exc:
            logger.exception("Error processing webhook payload: %s", exc)
            return web.Response(status=400, text="Bad Request")

    async def _health(request: web.Request) -> web.Response:
        return web.Response(status=200, text="OK")

    app.router.add_post("/", _handle_webhook)
    app.router.add_post("/webhook", _handle_webhook)
    app.router.add_get("/health", _health)

    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, host, port)
    await site.start()

    logger.info("Fluentd webhook listening on %s:%d", host, port)

    try:
        await asyncio.sleep(float("inf"))
    finally:
        await runner.cleanup()


if __name__ == "__main__":
    asyncio.run(main(asyncio.Queue(), {}))
