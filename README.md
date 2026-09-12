
# short explain
ProteaseDatasetGenerator — where positive data consists of N-mer segments spanning protease cleavage sites and negative data consists of randomly selected N-mer segments from non-cleavage regions

# explain
First, Protease datasets are made by this program. 
Second, other git repository, protease_sim_n_mer use these datasets for learning datasets and predict the cleavage probability scores on the spike protein of SARS-CoV-2 variants.

# Protease dataset generator - SOLID refactor

This project splits the original single Python script into small components with one responsibility each.

## Structure

```text
solid_refactored_protease_dataset/
├─ main.py                          # composition entry point
├─ protease_dataset/
│  ├─ application.py               # use-case orchestration
│  ├─ bootstrap.py                 # dependency wiring
│  ├─ config.py                    # configuration
│  ├─ domain.py                    # dataclasses / domain records
│  ├─ ports.py                     # Protocol interfaces
│  ├─ infrastructure/
│  │  ├─ csv_writer.py             # CSV persistence
│  │  ├─ mysql_repository.py       # MySQL cleavage-site source
│  │  ├─ static_repository.py      # legacy hard-coded substrate source
│  │  └─ uniprot_client.py         # UniProt REST client
│  └─ services/
│     ├─ uniprot_id.py             # UniProt ID normalization
│     ├─ sequence_processing.py    # positive/negative sequence math
│     ├─ positive_dataset.py       # positive dataset use case
│     └─ negative_dataset.py       # negative dataset use case
└─ tests/
   └─ test_sequence_processing.py
```

## Why this follows SOLID

- **S - Single Responsibility:** DB access, HTTP access, sequence processing, dataset generation, CSV writing, and application control are separate modules/classes.
- **O - Open/Closed:** Add another `CleavageSiteRepository`, `ProteinSequenceProvider`, or writer without editing the generation services.
- **L - Liskov Substitution:** `StaticCleavageSiteRepository` and `MySqlCleavageSiteRepository` expose the same repository contract.
- **I - Interface Segregation:** Services depend only on the narrow `ProteinSequenceProvider`; the application depends on the repository/writer contracts.
- **D - Dependency Inversion:** Core services depend on `Protocol` abstractions in `ports.py`, not MySQL, urllib, or pandas.

## Important behavior notes

1. The original program performs a MySQL query and then immediately overwrites that result with a hard-coded `list_subs`. Therefore the refactored default is `SUBSTRATE_SOURCE=static` to reproduce the *effective* active data source. Set `SUBSTRATE_SOURCE=mysql` to use the DB result instead.
2. Database credentials are **not hard-coded**. Set them through environment variables.
3. UniProt access uses the current REST FASTA endpoint: `https://rest.uniprot.org/uniprotkb/{id}.fasta`.
4. Negative generation groups all cleavage sites belonging to the same UniProt accession and excludes **all** corresponding positive windows. This intentionally corrects a likely bug in the original multiple-site branch, where the filtered indices are overwritten by the complete index list immediately before range detection.
5. Output filenames are kept close to the legacy names, including `df_no_nagative_data.csv` and `positive_pattern_aa_less_than_eight_...csv`, so downstream scripts are less likely to break.

## Run

Install dependencies:

```bash
pip install -r requirements.txt
```

Default (static substrate list):

```bash
python main.py
```

MySQL source, Linux/macOS example:

```bash
export SUBSTRATE_SOURCE=mysql
export MEROPS_DB_PASSWORD='your_password'
python main.py
```

Windows PowerShell:

```powershell
$env:SUBSTRATE_SOURCE = "mysql"
$env:MEROPS_DB_PASSWORD = "your_password"
python main.py
```

## Tests

The unit tests exercise the pure sequence logic without contacting MySQL or UniProt:

```bash
python -m unittest discover -s tests -v
```

## Original-to-new mapping

See [`MAPPING.md`](MAPPING.md) for a function-by-function responsibility map.

The UniProt provider is wrapped by `CachingProteinSequenceProvider`, so a protein such as `P51170` that appears at many cleavage sites is downloaded only once per run and reused by both positive and negative generation.
