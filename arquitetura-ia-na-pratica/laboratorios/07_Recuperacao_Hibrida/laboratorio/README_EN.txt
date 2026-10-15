R04 ENGLISH EDITION
English entry points select en-US explicitly. Original bilingual fixtures
and Portuguese entry points remain unchanged. See ENGLISH_EDITION_R04.txt.

CHAPTER 7 LAB — HYBRID RETRIEVAL
Python 3.10+ with sqlite3, standard library only. From laboratorio:
python -m unittest discover -v
python scenarios.py
python solutions_en.py

42 tests; 24 bilingual cases in 12 pairs; 3 variants; exercises 13 and 14.
Each variant evaluates 14 answerable and 10 negative/ambiguous questions.
Scenario and solution commands write results/, requiring a writable
directory. The database is in memory and contains no personal data.
corpus.json and cases.json are readable copies of fixtures.py constants.
Edit fixtures.py to change executable experiments and retain the previous
configuration before comparing outcomes.

Integration: pipeline.py, ingestion.sql, and base/ are unchanged copies
from Chapter 6. All sources pass through ingestion and activation.
retrieval.py adds BM25, concept vectors, cosine, RRF, context budgets,
extraction, and citation validation. Seven Acme documents plus one Zen
document, two languages: 16 chunks. Alice can query 6 per language and
cannot access payroll. Exercises retain Portuguese queries; English
counterparts are covered in the bilingual evaluation.

RESULTS AND LIMITS
Lexical and vector: 12/14 correct answers; hybrid: 14/14.
All variants: 10/10 expected negative/ambiguous decisions; zero citation
referential-integrity violations. Synthetic regression suite authored
with the representation, no held-out set. Not a trained-embedding
benchmark or evidence of generalization. Six manual concept features;
exact search; no ANN or external model. Pattern-based extraction does
not interpret arbitrary negation or conditions. An intact citation does
not establish universal semantic support. Four candidates per retriever;
up to three distinct-document chunks in 1100 JSON-context characters,
not tokens. Conflicts are checked only among retrieved candidates.
Trusted administrative methods; no HTTP endpoint, external action, or
API charge. Validation details are in ../Verificacao.json.
