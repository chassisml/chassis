from pathlib import Path

__VERSION__ = "0.1.0"

PACKAGE_ROOT = Path(__file__).parent
REPO_ROOT = PACKAGE_ROOT.parent

ASSET_BUNDLE = REPO_ROOT / "asset_bundle"

SRC = PACKAGE_ROOT / "src"

TESTS = PACKAGE_ROOT / "tests"
TEST_RESOURCES = TESTS / "resources"
TEST_CASES = ASSET_BUNDLE / __VERSION__ / "test_cases"

MODEL_YAML = ASSET_BUNDLE / __VERSION__ / "model.yaml"

GRPC_SERVER_PORT = 45000
