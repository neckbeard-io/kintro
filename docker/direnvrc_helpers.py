#!/usr/bin/env python3
import os
import os.path
import re
import sys


def main(args):
    requirements_file_path = args[1]
    (requirements_base_path, requirements_file) = (
        os.path.dirname(requirements_file_path),
        os.path.basename(requirements_file_path),
    )

    all_deps = resolve_dependencies(requirements_base_path, requirements_file)

    results = [(dep, is_mtime_newer(dep)) for dep in all_deps]

    if any(r[1] for r in results):
        print(" ".join(r[0] for r in results))
        sys.exit(1)
    sys.exit(0)


def resolve_dependencies(requirements_base_path, requirements_file):
    yield os.path.join(requirements_base_path, requirements_file)
    with open(os.path.join(requirements_base_path, requirements_file)) as f:
        for line in f.read().split("\n"):
            match = re.search("^[-]r", line)
            if match:
                req_import = match.string.split(" ")[1]
                yield os.path.join(requirements_base_path, req_import)
                yield from resolve_dependencies(requirements_base_path, req_import)


def is_mtime_newer(filename):
    txt_filename = os.path.splitext(filename)[0] + ".txt"
    return os.path.getmtime(filename) > os.path.getmtime(txt_filename)


if __name__ == "__main__":
    main(sys.argv)
