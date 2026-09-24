from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
WORKFLOW = (ROOT / ".github" / "workflows" / "assignment-03-ci-cd.yml").read_text(
    encoding="utf-8"
)


def test_quality_and_infrastructure_are_independent_parallel_jobs():
    infrastructure = WORKFLOW.split("  infrastructure:", 1)[1].split(
        "\n  production-image:", 1
    )[0]
    assert "needs:" not in infrastructure


def test_risky_infrastructure_checks_run_before_heavier_smoke_test():
    infrastructure = WORKFLOW.split("  infrastructure:", 1)[1].split(
        "\n  production-image:", 1
    )[0]
    assert infrastructure.index("Validate Docker Compose") < infrastructure.index(
        "Build pinned MinIO tool image"
    )
    assert infrastructure.index("Build pinned MinIO tool image") < infrastructure.index(
        "Build bootstrap development image"
    )
    assert infrastructure.index("Build bootstrap development image") < infrastructure.index(
        "Smoke test PostgreSQL, MinIO, and MLflow"
    )


def test_production_image_waits_for_quality_and_infrastructure():
    production = WORKFLOW.split("  production-image:", 1)[1]
    assert "needs:" in production
    assert "- quality" in production
    assert "- infrastructure" in production


def test_ci_never_publishes_container_images():
    assert "packages: write" not in WORKFLOW
    assert "docker/login-action" not in WORKFLOW
    assert "push: true" not in WORKFLOW
    assert "push: false" in WORKFLOW
