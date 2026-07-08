import argparse
import json
import platform
import subprocess
import sys
from typing import Dict, List

from runtime_feature_tests import (
    STATUS_NO_PROBADO,
    STATUS_OK,
    get_supported_features,
    run_named_test,
)

NTSTATUS = {
    0: STATUS_OK,

    0xC000001D: "ILLEGAL_INSTRUCTION",
    -1073741795: "ILLEGAL_INSTRUCTION",

    0xC0000005: "ACCESS_VIOLATION",
    -1073741819: "ACCESS_VIOLATION",

    0xC0000096: "PRIVILEGED_INSTRUCTION",
    -1073741674: "PRIVILEGED_INSTRUCTION",

    0xC00000FD: "STACK_OVERFLOW",
    -1073741571: "STACK_OVERFLOW",

    0xC0000409: "STACK_BUFFER_OVERRUN",
    -1073740791: "STACK_BUFFER_OVERRUN",

    0xC0000602: "FAIL_FAST_EXCEPTION",
    -1073740286: "FAIL_FAST_EXCEPTION",
}


def _status_from_return_code(return_code: int) -> str:
    return NTSTATUS.get(return_code, f"EXIT_{return_code}")


def _status_from_child_process(proc: subprocess.CompletedProcess[str]) -> str:
    stdout = (proc.stdout or "").strip()

    if stdout:
        return stdout

    return _status_from_return_code(proc.returncode)


def _collect_results() -> Dict[str, object]:
    rows: List[Dict[str, object]] = []

    for feature in get_supported_features():
        proc = subprocess.run(
            [sys.executable, __file__, "--feature", feature],
            capture_output=True,
            text=True,
        )

        rows.append(
            {
                "technology": feature,
                "status": _status_from_child_process(proc),
                "exit_code": proc.returncode,
            }
        )

    overall_pass = all(
        row["status"] in (STATUS_OK, STATUS_NO_PROBADO)
        for row in rows
    )

    return {
        "kind": "isa_runtime_test",
        "python": sys.executable,
        "platform": platform.platform(),
        "overall_pass": overall_pass,
        "rows": rows,
    }


def _print_text(payload: Dict[str, object]) -> None:
    print("Runtime ISA execution test")
    print(f"Python: {payload['python']}")
    print()

    for row in payload["rows"]:
        print(
            f"{row['technology']:16s}: "
            f"{row['status']:24s} "
            f"(exit={row['exit_code']})"
        )

    print()
    print("RESULT:", "PASS" if payload["overall_pass"] else "FAIL")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--feature", choices=sorted(get_supported_features()))
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    if args.feature:
        status = run_named_test(args.feature)
        print(status)
        return 0

    payload = _collect_results()

    if args.json:
        print(json.dumps(payload, ensure_ascii=True))
    else:
        _print_text(payload)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())