
from openbb_core.app.model.obbject import OBBject
from pyxll import xl_func, xl_arg_type, xl_return_type, plot


@xl_arg_type("obb.OBBject", "object")
def command_output_arg(arg: OBBject):
    if not isinstance(arg, OBBject):
        raise ValueError("Expected a 'OBBject' object.")
    return arg


@xl_return_type("obb.OBBject", "object")
def command_output_result(result: OBBject):
    # Check OBBjects for errors
    if isinstance(result, OBBject):
        error = getattr(result, "error", None)
        if error:
            raise RuntimeError(getattr(error, "message", None) or str(error))
    return result


@xl_func("obb.OBBject result: dataframe<index=True>", name="obb.get_dataframe")
def command_output_get_dataframe(result: OBBject):
    return result.to_dataframe()


@xl_func("obb.OBBject result: str", name="obb.show")
def command_output_plot(result: OBBject):
    chart = result.to_chart()
    plot(chart)
    return "[OK]"
