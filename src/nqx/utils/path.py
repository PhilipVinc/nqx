import os
import re
from pathlib import Path


def resolve_env_vars(path, environment=None):
    if isinstance(path, Path):
        path = str(path)
    # Use a regular expression to find all instances of $VAR or ${VAR}
    matches = re.findall(r"\$([A-Za-z0-9_]+)|\$\{([A-Za-z0-9_]+)\}", path)

    # For each match, replace it with the value of the environment variable
    for match in matches:
        # The re.findall function returns a tuple for each match, where one element is the matched string and the other is an empty string.
        # We use next(item for item in match if item) to get the non-empty element of the tuple.
        var = next(item for item in match if item)

        if environment is None:
            env_var_value = os.getenv(var)
        else:
            env_var_value = os.environ.get(var, environment.get(var, ""))

        # If the environment variable is not set, replace it with an empty string
        if env_var_value is None:
            env_var_value = ""

        # Replace the environment variable in the path with its value
        path = path.replace("$" + var, env_var_value)
        path = path.replace("${" + var + "}", env_var_value)

    if len(matches) == 0:
        return Path(path)
    else:
        return resolve_env_vars(path, environment)
