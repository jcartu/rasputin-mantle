from __future__ import annotations

import json
from pathlib import Path


def test_tauri_config_is_parseable_and_named() -> None:
    root = Path(__file__).resolve().parent.parent.parent
    config_path = root / "apps" / "desktop" / "src-tauri" / "tauri.conf.json"
    data = json.loads(config_path.read_text())

    assert data["productName"] == "Rasputin Mantle"
    assert data["identifier"] == "dev.rasputin.mantle"
    assert data["build"]["frontendDist"] == "../dist"
    assert data["build"]["devUrl"] == "http://localhost:1420"
    assert data["app"]["windows"][0]["title"] == "Rasputin Mantle"
    assert data["app"]["windows"][0]["width"] >= 960


def test_desktop_package_and_rust_entry_exist() -> None:
    root = Path(__file__).resolve().parent.parent.parent
    assert (root / "apps" / "desktop" / "package.json").exists()
    assert (root / "apps" / "desktop" / "index.html").exists()
    assert (root / "apps" / "desktop" / "src" / "main.tsx").exists()
    assert (root / "apps" / "desktop" / "src-tauri" / "Cargo.toml").exists()
    assert (root / "apps" / "desktop" / "src-tauri" / "src" / "main.rs").exists()
