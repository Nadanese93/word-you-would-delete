"""Write the Make.fun entry: the single word 'captcha'.

Writes exactly one word (no trailing newline) to
$MAKEFUN_OUTPUT_DIR/entry.txt (or /output/entry.txt if unset),
atomically via a temp file in the same directory + os.replace.
"""

import os
import sys
import tempfile

ENTRY = "captcha"


def main() -> int:
    word = ENTRY

    # Validation: UTF-8, 1-77 chars, exactly one word, not only whitespace.
    try:
        encoded = word.encode("utf-8")
    except UnicodeEncodeError as exc:
        raise SystemExit(f"entry is not valid UTF-8: {exc}") from exc
    if not (1 <= len(word) <= 77):
        raise SystemExit(
            f"entry must be 1-77 characters, got {len(word)}"
        )
    if not word.strip():
        raise SystemExit("entry must not be only whitespace")
    if any(ch.isspace() for ch in word):
        raise SystemExit("entry must be exactly one word (no whitespace inside)")

    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output"
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "entry.txt")

    fd, tmp_path = tempfile.mkstemp(
        dir=out_dir, prefix=".entry.", suffix=".tmp"
    )
    try:
        with os.fdopen(fd, "wb") as fh:
            fh.write(encoded)
            fh.flush()
            os.fsync(fh.fileno())
        os.replace(tmp_path, out_path)
    except BaseException:
        try:
            os.unlink(tmp_path)
        except OSError:
            pass
        raise

    # Read-back verification: the file on disk must hold exactly the
    # bytes we intended to write; refuse to report success otherwise.
    with open(out_path, "rb") as fh:
        on_disk = fh.read()
    if on_disk != encoded:
        raise SystemExit(
            f"read-back mismatch: wrote {len(encoded)} bytes, "
            f"disk holds {len(on_disk)} bytes"
        )

    print(f"wrote {out_path} ({len(encoded)} bytes)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
