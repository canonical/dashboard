# Copyright 2026 Canonical Ltd.
# See LICENSE file for licensing details.

"""Unit tests for the dashboard charm's custom functionality.

Tests cover: load-sample-data action (the only custom code on top of django-framework).
"""

import os
import pathlib
import sys
import unittest.mock

import ops
import pytest

mock_paas = unittest.mock.MagicMock()
mock_paas.django.Charm = ops.CharmBase
sys.modules["paas_charm"] = mock_paas
sys.modules["paas_charm.django"] = mock_paas.django

CHARM_DIR = pathlib.Path(__file__).parents[2]
sys.path.insert(0, str(CHARM_DIR / "src"))

os.environ["SCENARIO_SKIP_CONSISTENCY_CHECKS"] = "1"

import charm  # noqa: E402
import ops.testing  # noqa: E402


def _patch_parent(mgr):
    container_obj = mgr.charm.unit.get_container("django-app")
    mgr.charm._container = container_obj
    mgr.charm._workload_config = unittest.mock.MagicMock()
    mgr.charm._workload_config.app_dir = pathlib.PurePosixPath("/srv/app")
    return container_obj


class TestLoadSampleDataAction:
    """Test the load-sample-data action."""

    def test_load_sample_data_runs_loaddata(self):
        """load-sample-data executes Django loaddata command."""
        ctx = ops.testing.Context(charm.DashboardCharm, charm_root=CHARM_DIR)
        container = ops.testing.Container("django-app", can_connect=True)
        state = ops.testing.State(containers={container}, leader=True)

        with ctx(ctx.on.action("load-sample-data"), state) as mgr:
            container_obj = _patch_parent(mgr)
            mock_process = unittest.mock.MagicMock()
            mock_process.wait.return_value = None
            container_obj.exec = unittest.mock.MagicMock(return_value=mock_process)
            mgr.run()

            container_obj.exec.assert_called_once()
            call_args = container_obj.exec.call_args
            assert call_args[0][0] == [
                "python3", "manage.py", "loaddata", "initial_data.yaml"
            ]
            assert call_args[1]["working_dir"] == "/srv/app"
            assert call_args[1]["service_context"] == "django"

        assert ctx.action_results == {"result": "loaded sample data"}

    def test_load_sample_data_fails_on_exec_error(self):
        """load-sample-data action fails when exec raises an error."""
        ctx = ops.testing.Context(charm.DashboardCharm, charm_root=CHARM_DIR)
        container = ops.testing.Container("django-app", can_connect=True)
        state = ops.testing.State(containers={container}, leader=True)

        with pytest.raises(ops.testing.ActionFailed) as exc_info:
            with ctx(ctx.on.action("load-sample-data"), state) as mgr:
                container_obj = _patch_parent(mgr)
                container_obj.exec = unittest.mock.MagicMock(
                    side_effect=ops.pebble.APIError(
                        body={},
                        code=500,
                        status="Internal Server Error",
                        message="container not ready",
                    )
                )
                mgr.run()

        assert "unable to load sample data" in exc_info.value.message

    def test_load_sample_data_fails_on_change_error(self):
        """load-sample-data fails when process.wait() raises ChangeError."""
        ctx = ops.testing.Context(charm.DashboardCharm, charm_root=CHARM_DIR)
        container = ops.testing.Container("django-app", can_connect=True)
        state = ops.testing.State(containers={container}, leader=True)

        with pytest.raises(ops.testing.ActionFailed) as exc_info:
            with ctx(ctx.on.action("load-sample-data"), state) as mgr:
                container_obj = _patch_parent(mgr)
                mock_process = unittest.mock.MagicMock()
                mock_process.wait.side_effect = ops.pebble.ChangeError(
                    err="command failed",
                    change=unittest.mock.MagicMock(),
                )
                container_obj.exec = unittest.mock.MagicMock(
                    return_value=mock_process
                )
                mgr.run()

        assert "unable to load sample data" in exc_info.value.message
