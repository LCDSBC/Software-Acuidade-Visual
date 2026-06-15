from __future__ import annotations

from pathlib import Path

from optotipos_core.config import (
    export_backup,
    import_backup,
    load_config,
    load_profile,
    save_config_file,
    save_profile,
)


def test_default_config_and_save(tmp_path: Path) -> None:
    config = load_config(tmp_path)
    assert config.get("Distancia.txt", "Distancia") == "4"

    save_config_file("Distancia.txt", {"Distancia": "6", "Unidade": "m"}, tmp_path)
    updated = load_config(tmp_path)
    assert updated.get_float("Distancia.txt", "Distancia", 0) == 6


def test_profile_roundtrip_preserves_key_names(tmp_path: Path) -> None:
    save_config_file("Tela.txt", {"LarguraTelaMM": "600"}, tmp_path)
    profile = save_profile("Teste_4m", tmp_path)
    assert profile.exists()
    assert "LarguraTelaMM=600" in profile.read_text(encoding="utf-8")

    save_config_file("Tela.txt", {"LarguraTelaMM": "500"}, tmp_path)
    load_profile("Teste_4m.ini", tmp_path)
    assert load_config(tmp_path).get("Tela.txt", "LarguraTelaMM") == "600"


def test_backup_roundtrip(tmp_path: Path) -> None:
    save_config_file("Distancia.txt", {"Distancia": "5"}, tmp_path)
    backup = export_backup(tmp_path / "BackupCalibracao.opt", tmp_path)
    assert backup.exists()

    restored = tmp_path / "restored"
    import_backup(backup, restored)
    assert load_config(restored).get("Distancia.txt", "Distancia") == "5"
