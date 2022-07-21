#!/usr/bin/env python3

import sys
import shlex
import subprocess
import argparse
import os

from lib.ranges import Range
from lib.status import get_files_from_git_status


def parse_args(args):
    # The name of the function is used in error messages so we wrap it
    def index_or_range(*args, **kwargs):
        return Range.parse(*args, **kwargs)

    def is_range(arg):
        try:
            Range.parse(arg)
            return True
        except:
            return False

    args = args[:]

    # This allows ranges starting with a negative number to be handled
    # gracefully.
    taken_ranges = []
    while args and is_range(args[-1]):
        taken_ranges.append(Range.parse(args.pop()))

    parser = argparse.ArgumentParser(
        description="Looks at the list of files displayed by git-status and, "
        "after skipping staged changes, copies the files at the given "
        "positions to your clipboard."
    )
    parser.add_argument(
        "-",
        "-l",
        "--list",
        action="store_true",
        help="Print the available choices and their indices.",
    )
    parser.add_argument(
        "ranges",
        metavar="INDEX_OR_RANGE",
        type=index_or_range,
        nargs="*",
        help="An index or inclusive range (ex: `1:`, `1:3`).",
    )
    
    args = parser.parse_args(args)
    args.ranges.extend(taken_ranges)

    if not args.ranges:
        args.ranges.append(Range(0, 0))

    return args


def put_clipboard(text):
    pbcopy = "clip" if os.name == "nt" else "pbcopy"

    with subprocess.Popen(
        [pbcopy], stdin=subprocess.PIPE, encoding="utf8"
    ) as process:
        process.communicate(text)
        if process.returncode != 0:
            raise RuntimeError(f"{pbcopy} gave non-zero status")


def main_copy_ranges(ranges):
    all_files = get_files_from_git_status()

    selected_files = []
    for range_ in ranges:
        try:
            selected_files.extend(range_.extract(*all_files))
        except IndexError:
            print(f"Range out of bounds: {range_}")
            sys.exit(1)

    escaped_result = " ".join(shlex.quote(i) for i in selected_files)
    put_clipboard(escaped_result)

    print(f"Copied {escaped_result}")


def main_print_list():
    staged, unstaged = get_files_from_git_status()
    for index, path in enumerate(staged):
        print(f"-{len(staged) - index}. {path}")

    for index, path in enumerate(unstaged):
        print(f"index. {path}")


def main(parsed_args):
    if parsed_args.list:
        main_print_list()
    elif parsed_args.ranges:
        main_copy_ranges(parsed_args.ranges)


if __name__ == "__main__":
    main(parse_args(sys.argv[1:]))
