# Copyright 2026 Canonical Ltd.
# See LICENSE file for licensing details.

"""Unit tests for the dashboard charm's custom functionality."""

import pytest
from ops import testing

import charm

_LOADDATA_CMD = ["python3", "manage.py", "loaddata", "initial_data.yaml"]


class TestLoadSampleDataAction:
    """Test the load-sample-data action."""

    def test_load_sample_data_runs_loaddata(self):
        """load-sample-data executes Django loaddata command."""
        ctx = testing.Context(charm.DashboardCharm)
        container = testing.Container(
            "django-app",
            can_connect=True,
            execs={testing.Exec(_LOADDATA_CMD)},
        )
        state = testing.State(containers={container}, leader=True)

        ctx.run(ctx.on.action("load-sample-data"), state)

        exec_record = ctx.exec_history["django-app"][0]
        assert exec_record.command == _LOADDATA_CMD
        assert exec_record.working_dir is not None
        assert ctx.action_results == {"result": "loaded sample data"}

    def test_load_sample_data_fails_on_exec_error(self):
        """load-sample-data action fails when exec raises ExecError."""
        ctx = testing.Context(charm.DashboardCharm)
        container = testing.Container(
            "django-app",
            can_connect=True,
            execs={testing.Exec(_LOADDATA_CMD, return_code=1)},
        )
        state = testing.State(containers={container}, leader=True)

        with pytest.raises(testing.ActionFailed) as exc_info:
            ctx.run(ctx.on.action("load-sample-data"), state)

        assert "unable to load sample data" in exc_info.value.message

    def test_load_sample_data_fails_on_api_error(self):
        """load-sample-data fails when exec itself raises an APIError."""
        ctx = testing.Context(charm.DashboardCharm)
        container = testing.Container("django-app", can_connect=True)
        state = testing.State(containers={container}, leader=True)

        with pytest.raises(testing.ActionFailed) as exc_info:
            ctx.run(ctx.on.action("load-sample-data"), state)

        assert "unable to load sample data" in exc_info.value.message
