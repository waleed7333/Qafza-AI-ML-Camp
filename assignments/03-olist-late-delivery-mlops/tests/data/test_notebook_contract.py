import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
NOTEBOOKS = sorted((ROOT / "notebooks").glob("0[1-6]_*.ipynb"))


def first_code_cell_source(path: Path) -> str:
    notebook = json.loads(path.read_text(encoding="utf-8"))
    for cell in notebook["cells"]:
        if cell["cell_type"] == "code":
            return "".join(cell["source"])
    raise AssertionError(f"No code cell found in {path.name}")


def test_six_training_notebooks_are_present_and_docker_safe():
    assert len(NOTEBOOKS) == 6

    for notebook in NOTEBOOKS:
        source = first_code_cell_source(notebook)
        assert "required_project_paths" in source
        assert 'assert ROOT.name == "03-olist-late-delivery-mlops"' not in source


def test_notebook_01_has_standalone_database_defaults():
    source = first_code_cell_source(NOTEBOOKS[0])
    assert 'os.getenv("POSTGRES_USER", "qafza")' in source
    assert 'os.getenv("POSTGRES_PASSWORD", "qafza_dev_password")' in source
    assert 'os.getenv("POSTGRES_DB", "qafza_mlops")' in source
