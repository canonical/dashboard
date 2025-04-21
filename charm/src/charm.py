#!/usr/bin/env python3
# Copyright 2025 Ubuntu
# See LICENSE file for licensing details.

"""Django Charm entrypoint."""

import logging
import typing

import ops
import paas_charm.django

logger = logging.getLogger(__name__)


class DashboardCharm(paas_charm.django.Charm):
    """Django Charm service."""

    def __init__(self, *args: typing.Any) -> None:
        """Initialize the instance.

        Args:
            args: passthrough to CharmBase.
        """
        super().__init__(*args)
        self.framework.observe(self.on.load_sample_data_action, self._on_load_sample_data)

    def _on_load_sample_data(self, event: ops.ActionEvent):
        """Load the application's sample data, using a command in the Django container."""
        command = ["python3", "manage.py", "loaddata", "initial_data.yaml"]
        working_dir = str(self._workload_config.app_dir)
        try:
            process = self._container.exec(
                command,
                working_dir=working_dir,
                service_context="django",
            )
            process.wait()  # Raise an error if there was an error running the process.
        except (ops.pebble.APIError, ops.pebble.ChangeError, ops.pebble.ExecError):
            event.fail("unable to load sample data")
        event.set_results({"result": "loaded sample data"})


if __name__ == "__main__":
    ops.main(DashboardCharm)
