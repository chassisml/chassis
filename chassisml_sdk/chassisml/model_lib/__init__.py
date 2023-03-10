from pathlib import Path

PACKAGE_ROOT = Path(__file__).parent
REPO_ROOT = PACKAGE_ROOT.parent

SRC = PACKAGE_ROOT / "src"

TESTS = PACKAGE_ROOT / "tests"
TEST_RESOURCES = TESTS / "resources"
