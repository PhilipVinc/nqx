from typing import Optional

from nqx.core import PythonProviderType
from nqx.cli.config import get_config


def get_provider(provider: Optional[PythonProviderType] = None):
    if provider is None:
        config = get_config()
        provider = PythonProviderType(config["python_provider"])

    if provider == PythonProviderType.auto:
        provider = PythonProviderType.system

    if provider == PythonProviderType.system:
        from . import system

        return system
    else:
        raise ValueError(f"Unknown Python Provider {provider}")
