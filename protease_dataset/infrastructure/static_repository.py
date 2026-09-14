from __future__ import annotations

from typing import Sequence

from ..domain import CleavageSite


# This is the list that actually overrides the SQL result in the original script.
_STATIC_S01247 = (
    CleavageSite("A3R530", 320),
    CleavageSite("A3R534", 338),
    CleavageSite("F2P1E0", 338),
    CleavageSite("Q96T73", 255),
    CleavageSite("P51170", 135),
    CleavageSite("P51170", 136),
    CleavageSite("P51170", 137),
    CleavageSite("P51170", 138),
    CleavageSite("P51170", 153),
    CleavageSite("P51170", 168),
    CleavageSite("P51170", 170),
    CleavageSite("P51170", 172),
    CleavageSite("P51170", 178),
    CleavageSite("P51170", 179),
    CleavageSite("P51170", 180),
    CleavageSite("P51170", 181),
    CleavageSite("P51170", 189),
    CleavageSite("K9N5Q8", 887),
    CleavageSite("P0DTC2", 815),
    CleavageSite("P59594", 797),
    CleavageSite("O15393", 255),
)


class StaticCleavageSiteRepository:
    """Repository containing the active hard-coded substrate list from the legacy script."""

    def get_by_protease(self, protease_code: str) -> Sequence[CleavageSite]:
        if protease_code == "S01.247":
            return _STATIC_S01247
        raise KeyError(
            f"No static substrate list is defined for {protease_code}. "
            "Set SUBSTRATE_SOURCE=mysql or add a static mapping."
        )

    def close(self) -> None:
        return None
