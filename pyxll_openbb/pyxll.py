from .generate_wrappers import generate_wrappers
from pathlib import Path
from pyxll import get_config
import importlib.resources
import logging

_log = logging.getLogger(__name__)


def modules():
    """Entry point for PyXLL.
    """
    # Generate the pyxll_openbb.wrappers package if it doesn't already exist
    generate_wrappers(force=False)

    return [
        "pyxll_openbb.obbject",
        "pyxll_openbb.wrappers",
        "pyxll_openbb.ribbon"
    ]


def ribbon():
    """Entry point for PyXLL.
    """
    cfg = get_config()

    disable_ribbon = False
    if cfg.has_option("OPENBB", "disable_ribbon"):
        try:
            disable_ribbon = bool(int(cfg.get("OPENBB", "disable_ribbon")))
        except (ValueError, TypeError):
            _log.error("Unexpected value for OPENBB.disable_ribbon.")

    if disable_ribbon:
        return []

    ribbon = importlib.resources.read_text("pyxll_openbb.resources", "ribbon.xml")
    return [
        (None, ribbon)
    ]
