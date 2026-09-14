from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path


PROTEASE_NUMBERS: dict[str, int] = {
    "S01.247": 566,
    "S08.071": 741,
    "C01.032": 62,
    "S01.047": 503,
    "S01.021": 498,
    "S01.034": 502,
    "S01.087": 512,
    "S01.292": 578,
}


@dataclass(frozen=True)
class DatabaseConfig:
    host: str = "localhost"
    port: int = 3306
    user: str = "root"
    password: str = ""
    database: str = "meropsweb121"

    @classmethod
    def from_env(cls) -> "DatabaseConfig":
        return cls(
            host=os.getenv("MEROPS_DB_HOST", "localhost"),
            port=int(os.getenv("MEROPS_DB_PORT", "3306")),
            user=os.getenv("MEROPS_DB_USER", "root"),
            password=os.getenv("MEROPS_DB_PASSWORD", ""),
            database=os.getenv("MEROPS_DB_NAME", "meropsweb121"),
        )


@dataclass(frozen=True)
class AppConfig:
    target_protease: str = "S01.247"
    trim_len: int = 160
    random_seed: int = 42
    chunk_size: int = 500
    output_dir: Path = Path("./proteases")
    substrate_source: str = "static"
    request_timeout_sec: float = 30.0
    database: DatabaseConfig = field(default_factory=DatabaseConfig.from_env)

    @property
    def protease_turn(self) -> int:
        # The original script increments the mapped value once before generation.
        return PROTEASE_NUMBERS[self.target_protease] + 1

    @classmethod
    def from_env(cls) -> "AppConfig":
        return cls(
            target_protease=os.getenv("TARGET_PROTEASE", "S01.247"),
            trim_len=int(os.getenv("TRIM_LEN", "160")),
            random_seed=int(os.getenv("RANDOM_SEED", "42")),
            chunk_size=int(os.getenv("CSV_CHUNK_SIZE", "500")),
            output_dir=Path(os.getenv("OUTPUT_DIR", "./proteases")),
            substrate_source=os.getenv("SUBSTRATE_SOURCE", "static").lower(),
            request_timeout_sec=float(os.getenv("UNIPROT_TIMEOUT_SEC", "30")),
            database=DatabaseConfig.from_env(),
        )

    def validate(self) -> None:
        if self.target_protease not in PROTEASE_NUMBERS:
            raise ValueError(
                f"Unknown TARGET_PROTEASE={self.target_protease!r}. "
                f"Known values: {sorted(PROTEASE_NUMBERS)}"
            )
        if self.trim_len <= 0 or self.trim_len % 2 != 0:
            raise ValueError("TRIM_LEN must be a positive even integer.")
        if self.chunk_size <= 0:
            raise ValueError("CSV_CHUNK_SIZE must be > 0.")
        if self.substrate_source not in {"static", "mysql"}:
            raise ValueError("SUBSTRATE_SOURCE must be either 'static' or 'mysql'.")
        if self.substrate_source == "mysql" and not self.database.password:
            raise ValueError(
                "MEROPS_DB_PASSWORD is required when SUBSTRATE_SOURCE=mysql."
            )
