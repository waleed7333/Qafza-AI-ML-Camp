from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DOCKERFILE = (ROOT / "Dockerfile.minio").read_text(encoding="utf-8")


def test_minio_dockerfile_pins_release_versions_and_verifies_checksums():
    assert "MINIO_RELEASE=RELEASE.2025-09-07T16-13-09Z" in DOCKERFILE
    assert "MC_RELEASE=RELEASE.2025-08-13T08-35-41Z" in DOCKERFILE
    assert "dl.min.io/server/minio/release" in DOCKERFILE
    assert "dl.min.io/client/mc/release" in DOCKERFILE
    assert DOCKERFILE.count("sha256sum -c -") == 2
