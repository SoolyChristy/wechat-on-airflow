"""Lock license text, product description, and current venue acceptance copy."""

from __future__ import annotations

import tomllib
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
NON_VENUE_DAGS = {
    "HTTPS可用代理巡检",
    "HTTPS可用代理巡检_ydmap",
    "zacks_phone_daily_reboot",
    "airflow_db_cleanup",
    "appium_wx_msg_watcher_for_zacks",
}


def _venue_count() -> int:
    manifest = yaml.safe_load((ROOT / "config/active-components.yaml").read_text())
    target = yaml.safe_load((ROOT / "config/runtime-target.yaml").read_text())
    venue_ids = [
        item["dag_id"] for item in manifest["active_dags"] if item["dag_id"] not in NON_VENUE_DAGS
    ]
    expected = int(target["managed_services"]["webapp"]["expected_venue_count"])
    assert len(venue_ids) == expected
    assert len(venue_ids) == len(set(venue_ids))
    return expected


def test_license_and_readme_badges_are_mit() -> None:
    assert (ROOT / "LICENSE").read_text().startswith("MIT License\n")
    project = tomllib.loads((ROOT / "pyproject.toml").read_text())["project"]
    assert project["license"] == "MIT"
    description = project["description"].lower()
    assert "tennis" in description
    assert "postgresql" in description
    assert "智能客服" not in project["description"]

    for name in ("README.md", "README.en.md"):
        text = (ROOT / name).read_text()
        assert "License-MIT" in text
        assert "Apache%202.0" not in text
        assert "Apache License 2.0" not in text
        assert "MIT License" in text


def test_current_acceptance_matches_active_venue_dags() -> None:
    count = _venue_count()
    readme = (ROOT / "README.md").read_text()
    english = (ROOT / "README.en.md").read_text()
    agents = (ROOT / "AGENTS.md").read_text()
    architecture = (ROOT / "ARCHITECTURE.md").read_text()

    assert f"{count} 个活跃场馆 DAG" in readme
    assert f"{count} Shenzhen venue DAGs" in english
    assert f"all {count} active venue DAGs" in english
    assert f"{count} venue DAGs" in agents
    assert f"All {count} venue DAGs" in architecture
    assert "ignore_errors" not in (ROOT / "pyproject.toml").read_text()


def test_airflow_image_cryptography_pin_is_documented_separately() -> None:
    requirements = (ROOT / "docker/airflow/requirements.txt").read_text()
    policy = (ROOT / "docs/operations/dependency-policy.md").read_text()
    project = tomllib.loads((ROOT / "pyproject.toml").read_text())["project"]

    assert "cryptography==48.0.1" in requirements
    assert "cryptography==50.0.1" in project["dependencies"]
    assert "docker/airflow/requirements.txt" in policy
    assert "--no-deps" in policy
    assert "does not upgrade the image" in policy
