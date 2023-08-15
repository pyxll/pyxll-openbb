from .generate_wrappers import generate_wrappers


def modules():
    """Entry point for PyXLL.
    """
    # Generate the pyxll_openbb.wrappers package if it doesn't already exist
    generate_wrappers(force=False)

    return [
        "pyxll_openbb.wrappers",
        "pyxll_openbb.commands"
    ]
