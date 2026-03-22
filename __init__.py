"""wxforge — ML weather data pipeline plugin for Hermes Agent.

All-Rust pipeline: fetch → decode → compute → render → export training datasets.
"""

import logging
from . import schemas, tools

logger = logging.getLogger(__name__)


def register(ctx):
    """Register all wxforge tools."""

    schema_map = {s["name"]: s for s in schemas.ALL_SCHEMAS}

    _tools = {
        "wxf_fetch": tools.wxf_fetch,
        "wxf_decode": tools.wxf_decode,
        "wxf_scan": tools.wxf_scan,
        "wxf_calc": tools.wxf_calc,
        "wxf_render": tools.wxf_render,
        "wxf_plan": tools.wxf_plan,
        "wxf_build": tools.wxf_build,
        "wxf_models": tools.wxf_models,
    }

    for name, handler in _tools.items():
        ctx.register_tool(
            name=name,
            toolset="wxforge",
            schema=schema_map[name],
            handler=handler,
            check_fn=tools.check_wxforge,
        )

    logger.info("wxforge plugin loaded: %d tools", len(_tools))
