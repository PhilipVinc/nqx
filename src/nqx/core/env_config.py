import logging


class EnvConfig:
    def __init__(self, env: dict = None):
        if env is None:
            env = {}
        self.env = env

    def __repr__(self) -> str:
        return f"EnvConfig({self.env})"

    def copy(self):
        return EnvConfig(env=self.env.copy())

    def update(self, env_vars: dict[str, str]):
        for k, v in env_vars.items():
            logging.debug("Updating environment variable %s=%s", k, v)
            self.env[k] = v
