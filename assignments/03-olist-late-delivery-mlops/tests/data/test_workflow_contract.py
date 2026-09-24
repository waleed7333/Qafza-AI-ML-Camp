from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
WORKFLOW = (ROOT / ".github" / "workflows" / "assignment-03-ci-cd.yml").read_text(encoding="utf-8")
RELEASE_WORKFLOW = (ROOT / ".github" / "workflows" / "assignment-03-release.yml").read_text(
    encoding="utf-8"
)


def test_quality_and_infrastructure_are_independent_parallel_jobs():
    infrastructure = WORKFLOW.split("  infrastructure:", 1)[1].split("\n  production-image:", 1)[0]
    assert "needs:" not in infrastructure


def test_risky_infrastructure_checks_run_before_heavier_smoke_test():
    infrastructure = WORKFLOW.split("  infrastructure:", 1)[1].split("\n  production-image:", 1)[0]
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


def test_release_workflow_is_manual_only():
    trigger_section = RELEASE_WORKFLOW.split("permissions:", 1)[0]
    assert "workflow_dispatch:" in trigger_section
    assert "\n  push:" not in trigger_section
    assert "\n  pull_request:" not in trigger_section


def test_release_workflow_requires_main_and_separates_validation_from_publish():
    assert 'GITHUB_REF_NAME" != "main"' in RELEASE_WORKFLOW
    assert "needs: validate" in RELEASE_WORKFLOW
    assert "packages: write" in RELEASE_WORKFLOW


def test_release_workflow_uses_github_token_and_immutable_traceability_tags():
    assert "docker/login-action@v3" in RELEASE_WORKFLOW
    assert "secrets.GITHUB_TOKEN" in RELEASE_WORKFLOW
    assert "Refusing to overwrite existing immutable tag" in RELEASE_WORKFLOW
    assert 'sha_tag="sha-' in RELEASE_WORKFLOW


def test_release_workflow_publishes_with_supply_chain_metadata():
    assert "push: true" in RELEASE_WORKFLOW
    assert "provenance: mode=max" in RELEASE_WORKFLOW
    assert "sbom: true" in RELEASE_WORKFLOW
    assert "steps.build.outputs.digest" in RELEASE_WORKFLOW


def test_release_summary_uses_literal_markdown_without_shell_substitution():
    assert "printf --" in RELEASE_WORKFLOW
    assert "Version: `%s`" in RELEASE_WORKFLOW
    assert "Digest: `%s`" in RELEASE_WORKFLOW
    assert 'echo "- Version: `$VERSION`"' not in RELEASE_WORKFLOW
    assert 'echo "- Digest: `$DIGEST`"' not in RELEASE_WORKFLOW
