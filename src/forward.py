#!/usr/bin/env python3

import sys
import subprocess

from lib.status import get_files_from_git_status
from lib.ranges import Range

cached_files = None


def memoized_get_files_from_git_status():
    # pylint: disable=global-statement
    global cached_files

    if cached_files is None:
        cached_files = get_files_from_git_status()

    return cached_files


def maybe_replace_arg(arg):
    try:
        range_ = Range.parse(arg)
    except ValueError:
        return [arg]

    try:
        return range_.extract(*memoized_get_files_from_git_status())
    except IndexError:
        sys.exit(f"Range out of bounds: {range_}")


def main(args):
    replaced_args = []
    for arg in args:
        replaced_args.extend(maybe_replace_arg(arg))

    try:
        # pylint: disable=subprocess-run-check
        return_code = subprocess.run(["git", *replaced_args]).returncode
    except KeyboardInterrupt:
        return_code = 130

    sys.exit(return_code)


if __name__ == "__main__":
    main(sys.argv[1:])
