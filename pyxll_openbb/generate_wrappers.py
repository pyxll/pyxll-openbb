from openbb import obb
from openbb_core.app.model.obbject import OBBject
import pandas as pd
import datetime as dt
import inspect
import logging
import typing
import types
import sys
import os


_log = logging.getLogger(__name__)


def _get_type_signature(annotation):
    """Return the PyXLL type signature for a type based on a type annotation"""
    if annotation is pd.DataFrame:
        return "obb.DataFrame<index=True>"
    elif annotation is pd.Series:
        return "pandas.series<index=True>"
    elif annotation is dt.date:
        return "date"
    elif annotation is dt.datetime:
        return "datetime"
    elif annotation is dt.time:
        return "time"
    elif isinstance(annotation, type):
        if issubclass(annotation, OBBject):
            return "obb.OBBject"

    origin = typing.get_origin(annotation)
    if origin is typing.Annotated:
        args = typing.get_args(annotation)
        return _get_type_signature(args[0])

    elif origin in (typing.List, list, tuple):
        args = typing.get_args(annotation)
        item_type = _get_type_signature(args[0]) or "var"
        return f"{item_type}[]"

    elif origin is typing.Literal:
        return "str"

    elif origin is typing.Union:
        args =  typing.get_args(annotation)
        types = list(filter(None, (_get_type_signature(x) for x in args)))
        if types:
            if len(types) < len(args):
                types.append("var")

            # Sort so var types always appear last
            indices = {t: i for i, t in enumerate(types)}
            types = sorted(set(types), key=lambda x: len(types) if x.startswith("var") else indices[x])

            return f"union<{', '.join(types)}>"

def _generate_wrapper_for_function(func, path, wrapped=None):
    if wrapped is None:
        wrapped = func

    name = ".".join(path)
    return_type = None

    try:
        signature = inspect.signature(wrapped)
        return_type = _get_type_signature(signature.return_annotation)

        parameters = []
        for parameter in signature.parameters.values():
            if parameter.kind not in (inspect.Parameter.POSITIONAL_ONLY, inspect.Parameter.POSITIONAL_OR_KEYWORD):
                break
            parameters.append(parameter)

        decorators = [
            f"@xl_func(category=\"OpenBB\", name=\"{name}\", disable_function_wizard_calc=True)"
        ]

        for p in parameters:
            sig = _get_type_signature(p.annotation)
            if sig:
                decorators.append(f"@xl_arg(\"{p.name}\", \"{sig}\")")

        if return_type is not None:
            decorators.append(f"@xl_return(\"{return_type}\")")

        decorators = "\n".join(decorators)

        param_names = []
        param_strings = []
        for p in parameters:
            param_string = p.name
            if p.default != inspect.Parameter.empty:
               param_string += f"={repr(p.default)}"

            param_names.append(p.name)
            param_strings.append(param_string)

        wrapper = f"""
{decorators}
def {name.replace('.', '_')}({', '.join(param_strings)}):
    \"""{func.__doc__ if func.__doc__ else ""}\"""
    return {'.'.join(path)}({', '.join([p.name for p in parameters])})"""

        return wrapper

    except:
        _log.error(f"Error wrapping '{name}'", exc_info=True)
        raise


def _generate_wrappers_for_object(obj, path) -> str:
    """Generate wrapper functions for an object.

    :param obj: Object to inspect and generate wrapper functions for.
    :param path: Base path to add this object name to for the Excel function name.
    """
    # Generate wrapper functions for functions and methods
    if inspect.isfunction(obj) or inspect.ismethod(obj):
        return _generate_wrapper_for_function(obj, path)

    # Ignore builtin types
    if obj.__class__.__module__ == "builtins":
        return ""

    # Inspect object properties and traverse down generating wrappers
    wrappers = []
    for attr in dir(obj):
        if not attr.startswith("_"):
            prop = getattr(obj, attr)
            wrappers.append(_generate_wrappers_for_object(prop, path + [attr]))

    return "\n".join(wrappers)


def generate_wrappers(force: bool = False) -> str:
    """Create the OpenBB wrapper functions that are used
    to call the API from Excel.
    """
    if not force and "pyxll_openbb.wrappers" in sys.modules:
        _log.debug("pyxll_openbb.wrappers already exists")
        return sys.modules["pyxll_openbb.wrappers"]

    # Look for the wrappers to see if they already exist
    path = os.path.join(os.path.dirname(__file__), "wrappers.py")
    wrappers_source = None

    if os.path.exists(path) and not force:
        with open(path, "rt", encoding="utf-8") as fh:
            wrappers_source = fh.read()

    if not wrappers_source:
        _log.debug("Generating OpenBB wrappers...")
        wrappers = _generate_wrappers_for_object(obb, ["obb"])
        _log.debug("Finished generating OpenBB wrappers.")

        wrappers_source = f"""
'''
AUTOGENERATED CODE - DO NOT EDIT
'''
from openbb import obb
from pyxll import xl_func, xl_arg, xl_return
from pyxll_openbb import obbject
import datetime


{wrappers}
"""
        # Try to write the wrappers to re-use next time, but this will fail if
        # site-packages is read only. 
        try:
            with open(path, "wt", encoding="utf-8") as fh:
                print(wrappers_source, file=fh)
        except OSError:
            pass

    # Load the module from the source (which may or may not be saved)
    module = types.ModuleType("pyxll_openbb.wrappers")
    module.__file__ = path
    try:
        exec(wrappers_source, module.__dict__)
    except:
        # If the module failed to import and we might have used a cached
        # verison try recreating it.
        if not force:
            return generate_wrappers(force=True)
        
        # Otherwise fail
        raise

    # Update the package and sys modules
    import pyxll_openbb
    pyxll_openbb.wrappers = module
    sys.modules["pyxll_openbb.wrappers"] = module

    return module



if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    generate_wrappers(force=True)
