"""Smoke import tests until adapter contract tests land."""

from scripts.adapters.aws import AWSAdapter
from scripts.adapters.azure import AzureAdapter
from scripts.adapters.gcp import GCPAdapter


def test_adapters_instantiate() -> None:
    assert GCPAdapter().provider == "gcp"
    assert AWSAdapter().provider == "aws"
    assert AzureAdapter().provider == "azure"
