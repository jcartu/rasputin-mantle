from __future__ import annotations

import json
import os
import subprocess
import tomllib
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
DESKTOP_ROOT = REPO_ROOT / "apps" / "desktop"
TAURI_ROOT = DESKTOP_ROOT / "src-tauri"


def test_tauri_config_files_are_valid_for_desktop_launch() -> None:
    config_path = TAURI_ROOT / "tauri.conf.json"
    cargo_path = TAURI_ROOT / "Cargo.toml"

    assert config_path.exists(), "Tauri config is required to launch the desktop shell"
    assert cargo_path.exists(), "Cargo manifest is required to launch the Tauri binary"

    config = json.loads(config_path.read_text(encoding="utf-8"))
    cargo = tomllib.loads(cargo_path.read_text(encoding="utf-8"))

    assert config["$schema"].endswith("/config/2")
    assert config["productName"] == "Rasputin Mantle"
    assert config["identifier"] == "dev.mantle.rasputin"
    assert config["build"]["devUrl"] == "http://localhost:3000"
    assert config["build"]["frontendDist"] == "../dist"
    assert config["app"]["windows"][0]["title"] == "Rasputin Mantle"
    assert config["app"]["windows"][0]["width"] >= 960

    package = cargo["package"]
    assert package["name"] == "rasputin-mantle-desktop"
    assert package["edition"] == "2021"
    assert "tauri" in cargo["dependencies"]
    assert cargo["dependencies"]["tauri"]["version"] == "2"


def test_tauri_desktop_binary_launches_or_ci_uses_config_contract() -> None:
    binary_candidates = [
        TAURI_ROOT / "target" / "debug" / "rasputin-mantle-desktop",
        TAURI_ROOT / "target" / "release" / "rasputin-mantle-desktop",
    ]
    binary = next(
        (candidate for candidate in binary_candidates if candidate.exists() and os.access(candidate, os.X_OK)),
        None,
    )

    if binary is None:
        assert (TAURI_ROOT / "src" / "main.rs").exists()
        assert (TAURI_ROOT / "src" / "lib.rs").exists()
        assert (DESKTOP_ROOT / "package.json").exists()
        return

    result = subprocess.run(
        [str(binary), "--help"],
        capture_output=True,
        text=True,
        timeout=10,
        check=False,
    )
    output = f"{result.stdout}\n{result.stderr}"
    assert result.returncode in (0, 1)
    assert "Rasputin" in output or "tauri" in output.lower()
