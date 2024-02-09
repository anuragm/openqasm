"""
(Re)generates regression tests. Use this script when you have made intentional changes to
the grammar and you want them reflected in the regression test directory.
"""
import os
import pathlib
from typing import List, Union

import openqasm_reference_parser
import ruamel.yaml

yaml = ruamel.yaml.YAML(typ="rt")
yaml.default_flow_style = False

TEST_DIR = pathlib.Path(__file__).parent
REPO_DIR = TEST_DIR.parents[2]


def find_files(directory: Union[str, os.PathLike], suffix: str = "") -> List:
    """Recursively find all files in ``directory`` that end in ``suffix``.

    Args:
        directory: the (absolute) directory to search for the files.
        suffix: the string that filenames should end in to be returned.  Files
            without this suffix are ignored.  This is useful for limiting files
            to those with a particular extension.
        raw: If false (the default), the output elements are all
        ``pytest.param`` instances with nice ids.  If true, then only the file
        names are returned, without the wrapping parameter.

    Returns:
        By default, a list of ``pytest`` parameters, where the value is a string
        of the absolute path to a file, and the id is a string of the path
        relative to the given directory.  If ``raw`` is given, then just a list
        of the files as ``pathlib.Path`` instances.
    """
    directory = pathlib.Path(directory).absolute()

    return [
        str(pathlib.Path(root) / file)
        for root, _, files in os.walk(directory)
        for file in files
        if file.endswith(suffix)
    ]


def regenerate_reference_output():
    """
    Regenerates the reference YAML output.
    """
    for file in find_files(TEST_DIR / "reference", suffix=".yaml"):
        with open(file, "r") as fp:
            obj = yaml.load(fp)

        if not "source" in set(obj):
            print(f"Skipping file {file}. {set(obj)}")
            continue

        try:
            obj["reference"] = openqasm_reference_parser.pretty_tree(
                program=obj["source"]
            )
            with open(file, "w") as fp:
                yaml.dump(obj, fp)
        except Exception as exc:
            print(f"Failed to parse file {file}. Reason {exc}")
