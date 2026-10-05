from __future__ import annotations

import argparse
import json
import sys

from .build import Builder
from .declarations import BuildError


def main(argv=None):
    parser = argparse.ArgumentParser(description="Build a ProjectPack through a build-target pack")
    sub = parser.add_subparsers(dest="operation", required=True)
    for name in ("build", "check", "validate"):
        command = sub.add_parser(name)
        command.add_argument("project", help="Explicit ProjectPack .cpack path")
        command.add_argument("target", help="Declared target name")
        if name == "check":
            command.add_argument("pack", help="Namespace to compile against contracts only")
    args = parser.parse_args(argv)
    try:
        builder = Builder(args.project, args.target)
        result = builder.check(args.pack) if args.operation == "check" else getattr(builder, args.operation)()
        print(json.dumps(result, indent=2, sort_keys=True))
        return 0
    except BuildError as ex:
        print(str(ex), file=sys.stderr)
        print(json.dumps({"ok": False, "diagnostics": [ex.diagnostic]}, indent=2))
        return 1
    except (OSError, KeyError, TypeError, ValueError) as ex:
        print(json.dumps({"ok": False, "diagnostics": [{"severity": "error", "code": "BUILD_IO",
                                                      "message": str(ex)}]}, indent=2))
        return 1


if __name__ == "__main__":
    sys.exit(main())
