from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DOCKERFILE = (ROOT / "Dockerfile.minio").read_text(encoding="utf-8")


def test_minio_dockerfile_pins_release_versions_and_binary_digests():
    assert "MINIO_RELEASE=RELEASE.2025-09-07T16-13-09Z" in DOCKERFILE
    assert "MC_RELEASE=RELEASE.2025-08-13T08-35-41Z" in DOCKERFILE
    assert "github.com/minio/minio/releases/download" in DOCKERFILE
    assert "github.com/minio/mc/releases/download" in DOCKERFILE
    assert "7c5bd8512c6e966455b1d198209358b2d191c77a83ab377c4073281065fb855f" in DOCKERFILE
    assert "01f866e9c5f9b87c2b09116fa5d7c06695b106242d829a8bb32990c00312e891" in DOCKERFILE
    assert DOCKERFILE.count("sha256sum -c -") == 2
