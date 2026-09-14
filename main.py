from __future__ import annotations

import time

from protease_dataset.bootstrap import build_application
from protease_dataset.config import AppConfig


def main() -> None:
    started = time.perf_counter()
    config = AppConfig.from_env()
    app = build_application(config)
    try:
        summary = app.run()
    finally:
        app.close()

    elapsed = time.perf_counter() - started
    print("=== Dataset generation complete ===")
    print(summary)
    print(f"elapsed_seconds={elapsed:.3f}")
    print(f"elapsed_minutes={elapsed / 60:.3f}")


if __name__ == "__main__":
    main()
