from typing import Annotated
from enum import Enum

from .env_config import EnvConfig


class EnvType(str, Enum):
    cpu = "cpu"
    gpu = "gpu"
    gpu_mpi = "gpu-mpi"


class VenvProviderType(str, Enum):
    uv = "uv"
    mamba = "mamba"
    conda = "conda"
    modules = "modules"
    auto = "auto"
    none = "none"


ProviderType = VenvProviderType


class PythonProviderType(str, Enum):
    system = "system"
    modules = "modules"
    mamba = "mamba"
    auto = "auto"
