from __future__ import annotations

from urllib.request import Request, urlopen


class UniProtRestSequenceProvider:
    """Fetches amino-acid sequences from the UniProt REST API in FASTA format."""

    BASE_URL = "https://rest.uniprot.org/uniprotkb/{uniprot_id}.fasta"

    def __init__(self, timeout_sec: float = 30.0) -> None:
        self._timeout_sec = timeout_sec

    def get_sequence(self, uniprot_id: str) -> str:
        url = self.BASE_URL.format(uniprot_id=uniprot_id)
        request = Request(
            url,
            headers={"User-Agent": "protease-dataset-generator/1.0"},
        )
        with urlopen(request, timeout=self._timeout_sec) as response:
            text = response.read().decode("utf-8")

        lines = [line.strip() for line in text.splitlines() if line.strip()]
        if not lines or not lines[0].startswith(">"):
            raise ValueError(f"Unexpected FASTA response for UniProt ID {uniprot_id}")

        sequence = "".join(line for line in lines[1:] if not line.startswith(">"))
        if not sequence:
            raise ValueError(f"Sequence was not found for UniProt ID {uniprot_id}")
        return sequence
