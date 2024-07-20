"""Meltano ReData extension."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path
from typing import Any

import structlog
from meltano.edk import models
from meltano.edk.extension import ExtensionBase
from meltano.edk.process import Invoker, log_subprocess_error

log = structlog.get_logger()


class MissingProfileTypeError(Exception):
    """Missing profile type error."""

    pass


class ReData(ExtensionBase):
    """Extension implementing the ExtensionBase interface."""

    def __init__(self) -> None:
        """Initialize the extension.

        Raises:
            MissingProfileTypeError: If the profile type is not set.
        """
        self.redata_bin = "dbt"
        self.redata_ext_type = os.getenv("DBT_EXT_TYPE", None)
        if not self.redata_ext_type:
            raise MissingProfileTypeError("DBT_EXT_TYPE must be set")
        self.dbt_project_dir = Path(os.getenv("DBT_PROJECT_DIR", "transform"))
        self.dbt_profiles_dir = Path(
            os.getenv("DBT_PROFILES_DIR", self.dbt_project_dir / "profiles")
        )
        self.redata_invoker = Invoker(self.redata_bin, cwd=self.dbt_project_dir)
        self.skip_pre_invoke = (
            os.getenv("DBT_EXT_SKIP_PRE_INVOKE", "false").lower() == "true"
        )

    def invoke(self, command_name: str | None, *command_args: Any) -> None:
        """Invoke the underlying cli, that is being wrapped by this extension.

        Args:
            command_name: The name of the command to invoke.
            command_args: The arguments to pass to the command.
        """
        try:
            self.redata_invoker.run_and_log(command_name, *command_args)
        except subprocess.CalledProcessError as err:
            log_subprocess_error(
                f"redata {command_name}", err, "ReData invocation failed"
            )
            sys.exit(err.returncode)

    def describe(self) -> models.Describe:
        """Describe the extension.

        Returns:
            The extension description
        """
        # TODO: could we auto-generate all or portions of this from typer instead?
        return models.Describe(
            commands=[
                models.ExtensionCommand(
                    name="redata_extension", description="extension commands"
                ),
                models.InvokerCommand(
                    name="redata_invoker", description="pass through invoker"
                ),
            ],
        )
