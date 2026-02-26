from __future__ import annotations

import re

from flask import Flask, jsonify, render_template, request
import sympy as sp
from sympy.parsing.sympy_parser import (
    convert_xor,
    implicit_multiplication_application,
    parse_expr,
    standard_transformations,
)

app = Flask(__name__)

TRANSFORMATIONS = standard_transformations + (
    implicit_multiplication_application,
    convert_xor,
)

SAFE_GLOBALS = {"__builtins__": {}}
SAFE_LOCALS = {
    name: getattr(sp, name)
    for name in dir(sp)
    if not name.startswith("_")
}


def _log10(value: sp.Expr) -> sp.Expr:
    return sp.log(value, 10)


SAFE_LOCALS.update(
    {
        "e": sp.E,
        "sen": sp.sin,
        "ln": sp.log,
        "log10": _log10,
    }
)


def _to_bool(raw_value) -> bool:
    if isinstance(raw_value, bool):
        return raw_value
    if isinstance(raw_value, str):
        return raw_value.strip().lower() in {"1", "true", "yes", "on"}
    return bool(raw_value)


def _parse_expression(raw: str, variable: sp.Symbol) -> sp.Expr:
    local_scope = dict(SAFE_LOCALS)
    local_scope[variable.name] = variable
    return parse_expr(
        raw,
        local_dict=local_scope,
        global_dict=SAFE_GLOBALS,
        transformations=TRANSFORMATIONS,
    )


@app.get("/")
def home() -> str:
    return render_template("index.html")


@app.post("/integrate")
def integrate():
    data = request.get_json(silent=True) or {}

    function_raw = str(data.get("function", "")).strip()
    variable_raw = str(data.get("variable", "x")).strip()
    mode = str(data.get("mode", "indefinite")).strip().lower()
    lower_raw = str(data.get("lower", "")).strip()
    upper_raw = str(data.get("upper", "")).strip()
    approximate = _to_bool(data.get("approximate", False))

    if not function_raw:
        return jsonify({"ok": False, "error": "Debes ingresar una función."}), 400

    if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", variable_raw):
        return (
            jsonify(
                {
                    "ok": False,
                    "error": "La variable debe ser un identificador válido, por ejemplo x.",
                }
            ),
            400,
        )

    variable = sp.Symbol(variable_raw)

    try:
        function_expr = _parse_expression(function_raw, variable)

        if mode == "defined":
            if not lower_raw or not upper_raw:
                return (
                    jsonify(
                        {
                            "ok": False,
                            "error": "Para una integral definida debes indicar límite inferior y superior.",
                        }
                    ),
                    400,
                )

            lower_expr = _parse_expression(lower_raw, variable)
            upper_expr = _parse_expression(upper_raw, variable)
            integral_expr = sp.Integral(function_expr, (variable, lower_expr, upper_expr))
            result_expr = sp.integrate(function_expr, (variable, lower_expr, upper_expr))
        else:
            integral_expr = sp.Integral(function_expr, variable)
            result_expr = sp.integrate(function_expr, variable)

        response = {
            "ok": True,
            "integral_latex": sp.latex(integral_expr),
            "result_latex": sp.latex(result_expr),
            "result_text": str(result_expr),
        }

        if mode == "defined" and approximate:
            numeric_expr = sp.N(result_expr, 25)
            if numeric_expr.has(sp.Integral):
                numeric_expr = sp.N(integral_expr, 25)

            if numeric_expr.has(sp.Integral):
                raise ValueError("No se pudo aproximar numéricamente esta integral.")

            response["numeric_latex"] = sp.latex(numeric_expr)
            response["numeric_text"] = str(numeric_expr)

        return jsonify(response)
    except Exception as exc:
        return jsonify({"ok": False, "error": f"No se pudo interpretar la expresión: {exc}"}), 400


if __name__ == "__main__":
    app.run(debug=True)
