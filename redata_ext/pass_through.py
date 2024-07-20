"""Passthrough shim for ReData extension."""

import sys

import structlog
from meltano.edk.logging import pass_through_logging_config
from redata_ext.extension import ReData


def pass_through_cli() -> None:
    """Pass through CLI entry point."""
    pass_through_logging_config()
    ext = ReData()
    ext.pass_through_invoker(
        structlog.getLogger("redata_invoker"),
        *sys.argv[1:] if len(sys.argv) > 1 else [],
    )
