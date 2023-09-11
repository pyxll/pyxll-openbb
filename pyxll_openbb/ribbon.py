from .generate_wrappers import generate_wrappers
from pyxll import rebind, schedule_call, xlcAlert


def update_wrappers(*args):
    """Update the OpenBB wrapper functions."""
    generate_wrappers(force=True)
    rebind()
    schedule_call(xlcAlert, "OpenBB wrappers updated")
