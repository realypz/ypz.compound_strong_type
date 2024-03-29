# -*- coding: utf-8 -*-
import glob
import os
import pathspec  # TODO: No module named 'pathspec'
import re


def _generate_macro(file_path: str) -> str:
    """
    Generate the macro from a file name.

    Args:
        file_path: the relative path of a file.

    Return:
        The generated macro.
    """
    assert file_path.endswith(".h") or file_path.endswith(".hpp")
    return re.sub("[/\.]", "_", file_path.upper()) + "_"


def _read_lines(file_path: str) -> str:
    """Read a file and return lines

    Args:
        file_path: the relative path of a file.

    Return:
        list of strings, each element has a content of one line.
    """
    with open(file_path) as f:
        lines = f.readlines()
    return lines


def _generate_or_fix_header_guard(lines, macro: str):
    IFNDEF = f"#ifndef {macro}\n"
    DEFINE = f"#define {macro}\n"
    ENDIF = f"#endif // {macro}\n"

    # "no guard" means no header pattern is found at all.

    ifndef_line_nr = None
    define_line_nr = None
    endif_line_nr = None

    ifndef_ok = False
    define_ok = False
    endif_ok = False

    for line_number, line_content in enumerate(lines, 0):
        if line_content.startswith("#ifndef"):
            ifndef_line_nr = line_number
            if line_content == IFNDEF:
                ifndef_ok = True

            # When the ifndef_line_nr is valid, check "#define ".
            if lines[ifndef_line_nr + 1].startswith("#define"):
                define_line_nr = ifndef_line_nr + 1
                if lines[ifndef_line_nr + 1] == DEFINE:
                    define_ok = True

        if line_content.startswith("#endif"):
            endif_line_nr = line_number
            if line_content == ENDIF:
                endif_ok = True

    if ifndef_line_nr != None and ifndef_ok == False:
        lines[ifndef_line_nr] = IFNDEF
        ifndef_ok = True

    if define_line_nr != None and define_ok == False:
        lines[define_line_nr] = DEFINE
        define_ok = True

    if endif_line_nr != None and endif_ok == False:
        lines[endif_line_nr] = ENDIF
        endif_ok = True

    if (ifndef_ok and define_ok and endif_ok) == False:
        lines.insert(0, f"#ifndef {macro}\n")
        lines.insert(1, f"#define {macro}\n")
        lines.append(f"#endif // {macro}\n")


def header_guard(file_path: str) -> None:
    macro = _generate_macro(file_path)
    lines = _read_lines(file_path)
    _generate_or_fix_header_guard(lines, macro)

    with open(file_path, "w") as f:
        for line in lines:
            f.write(line)


def list_header_files(base_dir: str) -> list[str]:  # TODO: make `base_dir` available.
    gitignore_spec = pathspec.PathSpec.from_lines(
        pathspec.patterns.GitWildMatchPattern, open(".gitignore")
    )
    hdrs = glob.glob("**/*.h", recursive=True)
    files_names = [file for file in hdrs if not gitignore_spec.match_file(file)]
    return files_names


if __name__ == "__main__":
    base_dir = os.getcwd()
    hdrs = list_header_files(base_dir)

    for hdr in hdrs:
        header_guard(hdr)