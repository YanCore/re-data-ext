"""ReData cli entrypoint."""

import os
import sys
from typing import List

import structlog
import typer  # type: ignore
from meltano.edk.extension import DescribeFormat
from meltano.edk.logging import default_logging_config, parse_log_level
from redata_ext.extension import ReData

APP_NAME = "ReData"

log = structlog.get_logger(APP_NAME)

ext = ReData()

# remove to enable stylized help output when `rich` is installed
typer.core.rich = None  # type: ignore
app = typer.Typer(
    name=APP_NAME,
    pretty_exceptions_enable=False,
)


@app.command()
def initialize(
    ctx: typer.Context,
    force: bool = typer.Option(False, help="Force initialization (if supported)"),
) -> None:
    """Initialize the ReData plugin."""
    try:
        ext.initialize(force)
    except Exception:
        log.exception(
            "initialize failed with uncaught exception, please report to maintainer",
        )
        sys.exit(1)


@app.command(
    context_settings={"allow_extra_args": True, "ignore_unknown_options": True}
)
def invoke(ctx: typer.Context, command_args: List[str]) -> None:
    """Invoke the plugin.

    Note: that if a command argument is a list, such as command_args,
    then unknown options are also included in the list and NOT stored in the
    context as usual.
    """
    command_name, command_args = command_args[0], command_args[1:]
    log.debug(
        "called",
        command_name=command_name,
        command_args=command_args,
        env=os.environ,
    )
    ext.pass_through_invoker(log, command_name, *command_args)


@app.command()
def describe(
    output_format: DescribeFormat = typer.Option(
        DescribeFormat.text,
        "--format",
        help="Output format",
    ),
) -> None:
    """Describe the available commands of this extension."""
    try:
        typer.echo(ext.describe_formatted(output_format))
    except Exception:
        log.exception(
            "describe failed with uncaught exception, please report to maintainer",
        )
        sys.exit(1)


@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    log_level: str = typer.Option("INFO", envvar="LOG_LEVEL"),
    log_timestamps: bool = typer.Option(
        False,
        envvar="LOG_TIMESTAMPS",
        help="Show timestamp in logs",
    ),
    log_levels: bool = typer.Option(
        False,
        "--log-levels",
        envvar="LOG_LEVELS",
        help="Show log levels",
    ),
    meltano_log_json: bool = typer.Option(
        False,
        "--meltano-log-json",
        envvar="MELTANO_LOG_JSON",
        help="Log in the meltano JSON log format",
    ),
) -> None:
    """Simple Meltano extension that wraps the re_data CLI."""
    default_logging_config(
        level=parse_log_level(log_level),
        timestamps=log_timestamps,
        levels=log_levels,
        json_format=meltano_log_json,
    )
