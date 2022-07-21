import os
import subprocess
import re

_STATUS_RE = re.compile(r"^.(?P<action>.) (?:.+ -> (?P<renamed_to>.+)|(?P<path>.+))$")


def relpaths(lst, root):
    return [os.path.relpath(os.path.join(root, i)) for i in lst]



def get_files_from_git_status():
    git_root = subprocess.check_output(
        ["git", "rev-parse", "--show-toplevel"], encoding="utf8"
    ).strip()

    staged = []
    unstaged = []

    output = subprocess.check_output(["git", "status", "--porcelain"], encoding="utf8")
    for line in output.splitlines():
        match = _STATUS_RE.match(line)
        if match:
            path = match.group("renamed_to") or match.group("path")

            if match.group("action") == " ":
                staged.append(path.strip())
            else:
                unstaged.append(path.strip())

    return (relpaths(staged, git_root), relpaths(unstaged, git_root))
