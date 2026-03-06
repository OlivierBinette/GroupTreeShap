from pathlib import Path

from testbook import testbook

PROJECT_ROOT = Path(__file__).parent.parent.parent


@testbook(PROJECT_ROOT / "analyses" / "validate-against-xgboost.ipynb", execute=True)
def test_validate_python_implementations(tb):
    pass
