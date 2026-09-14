
# Q: こちらのプログラムをSOLID原則によって機能ごとにプログラム ファイルを分割してくださいクラスを必要に応じて利用して良いです
03_creating_positive&negative_data_160aa_refactoring_20260123.py


SOLID原則に沿って、元の約800行のPythonプログラムを機能別に分割した版を作成しました。元コードではPositive生成だけでもUniProt ID処理、UniProt通信、配列切り出し、DataFrame操作、CSV保存まで一つの関数が担当しており、Negative生成も同様に複数責務を持っていました。 

**完成版はこちらです。**

[SOLIDリファクタリング版一式をダウンロード](sandbox:/mnt/data/solid_refactored_protease_dataset.zip)

[README.md](sandbox:/mnt/data/solid_refactored_protease_dataset/README.md)
[元関数 → 新ファイル対応表 MAPPING.md](sandbox:/mnt/data/solid_refactored_protease_dataset/MAPPING.md)

主な構成は次のようにしました。

* `main.py` — 起動処理のみ
* `application.py` — Positive/Negative生成全体のオーケストレーション
* `config.py` — `trim_len=160`、protease、DB設定など
* `domain.py` — `CleavageSite`, `PositiveRecord`, `NegativeRecord` などのデータクラス
* `ports.py` — `Protocol`による抽象インターフェース
* `services/positive_dataset.py` — Positiveデータ生成
* `services/negative_dataset.py` — Negativeデータ生成
* `services/sequence_processing.py` — 160 aa切り出し、padding、Negative候補領域計算
* `services/uniprot_id.py` — UniProt IDの正規化
* `infrastructure/uniprot_client.py` — UniProt通信
* `infrastructure/cached_sequence_provider.py` — 同じUniProt配列の再取得防止
* `infrastructure/mysql_repository.py` — MySQLアクセス
* `infrastructure/static_repository.py` — 元コードのハードコードされた`list_subs`
* `infrastructure/csv_writer.py` — CSV保存だけを担当
* `bootstrap.py` — 各クラスを組み合わせるDependency Injection部分
* `tests/` — 外部DBやUniProtに接続せず検証できる単体テスト

### SOLIDとの対応

**S: Single Responsibility Principle**
DB、UniProt、配列処理、Positive生成、Negative生成、CSV出力、実行制御を別クラスへ分離しました。

**O: Open/Closed Principle**
たとえば将来UniProtではなくローカルFASTAから配列を取得したい場合でも、

```python
class ProteinSequenceProvider(Protocol):
    def get_sequence(self, uniprot_id: str) -> str:
        ...
```

を満たす新しいクラスを追加するだけで、`PositiveDatasetService`や`NegativeDatasetService`を書き換える必要がありません。

**L: Liskov Substitution Principle**
`StaticCleavageSiteRepository`と`MySqlCleavageSiteRepository`は同じRepositoryインターフェースとして交換できます。

**I: Interface Segregation Principle**
Positive/Negative生成クラスはMySQLやCSV writer全体を知る必要がなく、必要な`ProteinSequenceProvider`だけに依存します。

**D: Dependency Inversion Principle**
生成ロジックが

```text
MySQLdb
urllib
pandas
```

そのものに依存するのではなく、

```text
CleavageSiteRepository
ProteinSequenceProvider
DatasetResultWriter
```

という抽象に依存する構造にしています。

### 元コードから特に改善した点

元コードではMySQLから基質を取得した後、実際にはその結果を固定の`list_subs`で上書きしていました。
そのため今回のデフォルトは、

```text
SUBSTRATE_SOURCE=static
```

として、**現在の元コードが実際に使っているデータ**と同じ動作にしています。

MySQLを直接使いたければ、

```text
SUBSTRATE_SOURCE=mysql
```

へ変更するだけです。

また、元コードに直接記述されていたDB接続情報はリファクタリング版には埋め込まず、環境変数へ移しました。元コードではDB設定が`con_db()`内に直接存在していました。

UniProtについても旧URLではなく、現在UniProtが案内しているREST APIのFASTA取得形式、

```text
https://rest.uniprot.org/uniprotkb/{ID}.fasta
```

を使うようにしています。UniProt公式ドキュメントでも個別エントリを`.fasta`で取得するREST URLが案内されています。([UniProt][1])

### Negativeデータ生成について重要な修正

元プログラムには複数の開裂位置を除外する処理で、

```python
remain_index_list = df_index[and_cond_list]
```

とした直後に、

```python
remain_index_list = df_index['index_list'].tolist()
```

としており、せっかく除外したインデックスを全インデックスへ戻している箇所があります。

これはNegativeデータへ既知の開裂領域が混ざる可能性があるため、今回の版では、

```text
UniProt ID
   ↓
そのタンパク質の全P1をまとめる
   ↓
P1 ± 80 aa をすべて除外
   ↓
残った連続領域から160 aa Negativeを生成
```

という構造に修正しました。

たとえば`P51170`には元データ上、

```text
135
136
137
138
153
168
...
189
```

のように複数のP1が存在しますが、これらを**すべてまとめて除外した上でNegativeを作成**します。

さらに`P51170`をPositive生成で何度も利用していても、`CachingProteinSequenceProvider`によりUniProtから同じ配列を何度もダウンロードしません。

### 動作確認

構文チェックに加え、以下を含む**10個の単体テストをすべてPASS**しています。

```text
Ran 10 tests
OK
```

Positiveの中央切り出し、末端padding、UniProt ID正規化、複数P1の除外、Negative領域への開裂部位混入防止、UniProt配列キャッシュまで確認しています。

実行は展開後、

```bash
pip install -r requirements.txt
python main.py
```

です。

今回の構成にしておくと、次に「Positive/Negative生成アルゴリズム自体をStrategyパターンにする」「MySQLではなくCSV/FASTAを入力にする」「pytestで完全なテスト環境を構築する」といった変更も、既存コードを大きく壊さず追加できるようになります。

[1]: https://www.uniprot.org/help/api_retrieve_entries?utm_source=chatgpt.com "Programmatic access - Retrieving individual entries | UniProt help"


