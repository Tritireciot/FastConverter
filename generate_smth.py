import argparse
import json
from typing import Any, Callable, MutableMapping, Sequence


def generate_latex_view(params: MutableMapping[str, Any]) -> MutableMapping[str, Any]:
    operation = params.get("TsampMathOp", "+")
    formula = r"\textrm{Ts}"
    match operation:
        case "1/Ts Only":
            formula = "1/" + formula
        case "Ts Only":
            pass
        case _:
            formula = "u" + operation + formula
    return {
        "form": {"width": 50, "value": "rectangle", "height": 50},
        "displayProperties": {"latex": "{" + formula + "}"},
    }


def get_algorithm():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "algorithm",
        type=str,
        help="Algorithm which would be used to generate view",
    )
    match parser.parse_args().algorithm:
        case "Base":
            return generate_latex_view
        case _:
            raise NotImplementedError("Algorithm not supported")


def main() -> None:
    params = json.loads(input())
    algorithm = get_algorithm()
    print(json.dumps(algorithm(params)))


if __name__ == "__main__":
    main()
