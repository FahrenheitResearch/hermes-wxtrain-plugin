"""wxtrain — ML weather data pipeline plugin for Hermes Agent.

All-Rust pipeline: fetch → decode → compute → render → export training datasets.
"""

import logging
from . import schemas, tools

logger = logging.getLogger(__name__)


def register(ctx):
    """Register all wxtrain tools."""

    schema_map = {s["name"]: s for s in schemas.ALL_SCHEMAS}

    _tools = {
        "wxt_fetch": tools.wxt_fetch,
        "wxt_decode": tools.wxt_decode,
        "wxt_scan": tools.wxt_scan,
        "wxt_calc": tools.wxt_calc,
        "wxt_render": tools.wxt_render,
        "wxt_plan": tools.wxt_plan,
        "wxt_build": tools.wxt_build,
        "wxt_models": tools.wxt_models,
    }

    for name, handler in _tools.items():
        ctx.register_tool(
            name=name,
            toolset="wxtrain",
            schema=schema_map[name],
            handler=handler,
            check_fn=tools.check_wxtrain,
        )

    logger.info("wxtrain plugin loaded: %d tools", len(_tools))
