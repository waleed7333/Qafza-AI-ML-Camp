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
    assert '"http://localhost:9000/minio/health/live"' in COMPOSE
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


def test_minio_services_use_project_built_tool_image():
    minio = COMPOSE.split("  minio:", 1)[1].split("\n\n  minio-init:", 1)[0]
    minio_init = COMPOSE.split("  minio-init:", 1)[1].split("\n\n  mlflow:", 1)[0]
    for service in [minio, minio_init]:
        assert "dockerfile: Dockerfile.minio" in service
        assert "image: qafza-assignment-03-minio:local" in service
