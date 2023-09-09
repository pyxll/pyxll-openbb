
from openbb_core.app.model.obbject import OBBject
from pyxll import xl_func, xl_arg_type, xl_return_type, get_type_converter, plot


@xl_arg_type("obb.OBBject", "object")
def obbject_from_xl_arg(arg: OBBject):
    if not isinstance(arg, OBBject):
        raise ValueError("Expected a 'OBBject' object.")
    return arg


@xl_return_type("obb.OBBject", "object")
def obbject_to_xl_return(result: OBBject):
    # Check OBBjects for errors
    if isinstance(result, OBBject):
        error = getattr(result, "error", None)
        if error:
            raise RuntimeError(getattr(error, "message", None) or str(error))
    return result


@xl_func("obb.OBBject result: dataframe<index=True>", name="obb.to_dataframe")
def obbject_to_dataframe(result: OBBject):
    return result.to_dataframe()


@xl_func("obb.OBBject result: str", name="obb.to_chart")
def obbject_to_chart(result: OBBject):
    chart = result.to_chart()
    plot(chart)
    return "[OK]"


@xl_arg_type("obb.DataFrame", "union<var[][], object>")
def dataframe_from_xl_arg(arg, index=None):
    print("dataframe_from_xl_arg called")
    print(arg)
    print(type(arg))

    if isinstance(arg, OBBject):
        return arg.to_dataframe()

    to_dataframe = get_type_converter("var", "pandas.dataframe", dest_kwargs={"index": index})
    return to_dataframe(arg)


@xl_return_type("obb.DataFrame", "pandas.dataframe")
def dataframe_to_xl_return(arg, index=None):
    if isinstance(value, OBBject):
        value = value.to_dataframe()
    to_var = get_type_converter("pandas.dataframe", "var", src_kwargs={"index": index})
    return to_var(value)
