# Mapping from the original script to the SOLID refactor

| Original responsibility/function | Refactored location | Reason |
|---|---|---|
| `main()` | `main.py`, `application.py` | Entry point and orchestration are separated. |
| `con_db()` | `infrastructure/mysql_repository.py` | MySQL is infrastructure, not dataset logic. |
| `aaseq_from_uid()` | `infrastructure/uniprot_client.py` | HTTP/UniProt access is isolated behind `ProteinSequenceProvider`. |
| UniProt ID regex repeated in positive/negative functions | `services/uniprot_id.py` | One normalization rule, reused by both services. |
| Cleavage-window slicing/padding | `services/sequence_processing.py` | Pure sequence math is independently testable. |
| Negative-region detection/random window extraction | `services/sequence_processing.py` | Shared deterministic sequence logic. |
| `create_posi_dataset()` | `services/positive_dataset.py` | Positive generation has one responsibility. |
| `create_nega_dataset()` | `services/negative_dataset.py` | Negative generation has one responsibility. |
| `DataFrame.to_csv()` calls scattered through loops | `infrastructure/csv_writer.py` | Persistence/file naming is isolated. |
| Hard-coded `list_subs` | `infrastructure/static_repository.py` | The legacy static source implements the same repository interface as MySQL. |
| MySQL-vs-static choice and object construction | `bootstrap.py` | Dependency composition is centralized. |
| Hard-coded settings and DB credentials | `config.py` + environment variables | Configuration is separated from business logic; credentials are not committed. |
| repeated UniProt download for the same accession | `infrastructure/cached_sequence_provider.py` | Decorator adds caching without changing generation services. |

## Legacy code deliberately removed

`create_merops_code_table()` and `create_subs_count_list()` only load/print CSV metadata in the uploaded active code; their values do not affect the active generation path. They are therefore not included in the new core application. If they become required inputs later, they should be added as a separate repository/metadata-reader implementation rather than put back into `main.py`.
