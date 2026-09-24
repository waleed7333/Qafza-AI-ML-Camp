from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
COMPOSE = (ROOT / "compose.yaml").read_text(encoding="utf-8")


def test_minio_init_uses_container_environment_variables():
    required = [
        '"$$MINIO_ROOT_USER"',
        '"$$MINIO_ROOT_PASSWORD"',
        '"local/$$MLFLOW_ARTIFACT_BUCKET"',
        '"local/$$DVC_BUCKET"',
    ]
    for token in required:
        assert token in COMPOSE


def test_minio_init_waits_for_minio_health():
    assert 'test: ["CMD", "mc", "ready", "local"]' in COMPOSE
    minio_init = COMPOSE.split("  minio-init:", 1)[1].split("\n\n  mlflow:", 1)[0]
    assert "condition: service_healthy" in minio_init


def test_trainer_exposes_project_root_on_pythonpath():
    trainer = COMPOSE.split("  trainer:", 1)[1].split("\n\nvolumes:", 1)[0]
    assert "PYTHONPATH: /workspace" in trainer


def test_large_dvc_targets_are_git_ignored():
    gitignore = (ROOT / ".gitignore").read_text(encoding="utf-8")
    assert "data/raw/" in gitignore
    assert "artifacts/" in gitignore


def test_makefile_uses_local_no_scm_for_containerized_dvc():
    makefile = (ROOT / "Makefile").read_text(encoding="utf-8")
    assert "dvc config core.no_scm true --local" in makefile
    assert "dvc-status:" in makefile


def test_minio_images_are_pinned_to_official_docker_hub_digests():
    assert (
        "minio/minio:RELEASE.2025-09-07T16-13-09Z@sha256:"
        "14cea493d9a34af32f524e538b8346cf79f3321eff8e708c1e2960462bd8936e"
    ) in COMPOSE
    assert (
        "minio/mc:RELEASE.2025-08-13T08-35-41Z@sha256:"
        "a7fe349ef4bd8521fb8497f55c6042871b2ae640607cf99d9bede5e9bdf11727"
    ) in COMPOSE
