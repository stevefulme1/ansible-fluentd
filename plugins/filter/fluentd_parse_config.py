# -*- coding: utf-8 -*-

# Copyright: (c) 2024, Steve Fulmer (@stevefulme1)
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import re


def parse_fluentd_config(config_string):
    """Parse a Fluentd configuration string into structured data.

    Returns a list of directive dicts with keys:
      type (str): directive name (source, match, filter, system, label)
      tag (str or None): tag pattern for match/filter directives
      params (dict): key-value parameters
      children (list): nested directives
    """
    lines = config_string.splitlines()
    return _parse_block(lines, 0, len(lines))[0]


def _parse_block(lines, start, end):
    """Parse lines[start:end] into a list of directives."""
    directives = []
    i = start
    while i < end:
        line = lines[i].strip()

        if not line or line.startswith("#"):
            i += 1
            continue

        match = re.match(r"<(\w+)\s*(.*?)>", line)
        if match:
            directive_type = match.group(1)
            tag = match.group(2).strip() or None
            close_tag = "</%s>" % directive_type
            close_idx = _find_closing(lines, i + 1, end, directive_type)
            if close_idx is None:
                i += 1
                continue
            children, _end = _parse_block(lines, i + 1, close_idx)
            params = {}
            child_directives = []
            for child in children:
                if isinstance(child, dict) and "type" in child:
                    child_directives.append(child)
                elif isinstance(child, tuple):
                    params[child[0]] = child[1]

            directives.append(
                dict(
                    type=directive_type,
                    tag=tag,
                    params=params,
                    children=child_directives,
                )
            )
            i = close_idx + 1
            continue

        close_match = re.match(r"</\w+>", line)
        if close_match:
            i += 1
            continue

        kv_match = re.match(r"(\S+)\s+(.*)", line)
        if kv_match:
            directives.append((kv_match.group(1), kv_match.group(2).strip()))
            i += 1
            continue

        i += 1

    return directives, i


def _find_closing(lines, start, end, directive_type):
    """Find the index of the closing tag for a directive."""
    depth = 1
    for i in range(start, end):
        line = lines[i].strip()
        if re.match(r"<%s\b" % re.escape(directive_type), line):
            depth += 1
        elif line == "</%s>" % directive_type:
            depth -= 1
            if depth == 0:
                return i
    return None


class FilterModule:
    """Fluentd configuration parser filter."""

    def filters(self):
        return {
            "fluentd_parse_config": parse_fluentd_config,
        }
