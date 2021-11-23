import pytest
from pathlib import Path


def pytest_addoption(parser):
    parser.addoption(
        "--data-root", action="store", default=Path(__file__).parent.parent.joinpath("data"), help="root directory for gov data"
    )


@pytest.fixture
def data_root(request):
    return request.config.getoption("--data-root")