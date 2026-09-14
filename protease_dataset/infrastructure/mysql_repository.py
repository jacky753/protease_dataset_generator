from __future__ import annotations

from typing import Sequence

from ..config import DatabaseConfig
from ..domain import CleavageSite


class MySqlCleavageSiteRepository:
    """MySQL implementation of CleavageSiteRepository."""

    def __init__(self, config: DatabaseConfig) -> None:
        try:
            import MySQLdb as mydb
        except ImportError as exc:
            raise RuntimeError(
                "mysqlclient is required for SUBSTRATE_SOURCE=mysql. "
                "Install it with: pip install mysqlclient"
            ) from exc

        self._connection = mydb.connect(
            host=config.host,
            port=config.port,
            user=config.user,
            password=config.password,
            database=config.database,
        )

    def get_by_protease(self, protease_code: str) -> Sequence[CleavageSite]:
        cursor = self._connection.cursor()
        try:
            cursor.execute(
                "SELECT uniprot_acc, p1 FROM cleavage WHERE code = %s;",
                (protease_code,),
            )
            return tuple(
                CleavageSite(str(uniprot_acc), int(p1))
                for uniprot_acc, p1 in cursor.fetchall()
            )
        finally:
            cursor.close()

    def close(self) -> None:
        self._connection.close()
