import sys

if sys.version_info.minor >= 7:
    import importlib

    def import_from_path(path):
        spec = importlib.util.spec_from_file_location("module.name", path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

    old_python = False
elif sys.version_info.minor >= 6:
    import imp

    # import module
    def import_from_path(path):
        module = imp.load_source("module.name", path)
        return module

    old_python = True

else:
    raise NotImplementedError
