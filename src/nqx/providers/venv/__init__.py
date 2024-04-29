from typing import Optional

from nqx.core import VenvProviderType
from nqx.cli.config import get_config


def get_provider(provider: Optional[VenvProviderType] = None):
    if provider is None:
        config = get_config()
        provider = VenvProviderType(config["venv_provider"])

    if provider == VenvProviderType.uv:
        from . import uv

        return uv
    else:
        raise ValueError(f"Unknown provider {provider}")
