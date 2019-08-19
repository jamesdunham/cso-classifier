"""
Demonstrate the CSO Classifier on some CS articles in Web of Science.

We fetch a set of paper titles, abstracts and keywords from BigQuery, run the CSO Classifier over them, and write the
result to the `demo` directory as `demo-predictions.json`.
"""
import argparse
import json
from pathlib import Path

from classifier.classifier import run_cso_classifier_batch_mode
from cset.bigquery import run_query, flatten_row
from demo.settings import INPUT_PATH, OUTPUT_PATH, DEMO_DIR


def load_input() -> dict:
    """Read the classifier inputs from the disk, if already fetched; otherwise request from BigQuery."""
    if not INPUT_PATH.exists():
        print('Fetching from BigQuery')
        papers = run_query()
        INPUT_PATH.write_text(json.dumps(papers, indent='  '))
    papers = json.loads(INPUT_PATH.read_text())
    return papers


def write_output(predictions: dict, papers: dict) -> None:
    """Write predictions merged with original inputs to the disk."""
    for wos_id, prediction in predictions.items():
        prediction.update(**papers[wos_id])
    OUTPUT_PATH.write_text(json.dumps(predictions, indent='  ', sort_keys=True))


def main() -> None:
    """Demonstrate the CSO Classifier on some CS articles in Web of Science."""
    papers = load_input()
    # This is a SQL query for BigQuery that joins titles, abstracts, and keywords from  Web of Science
    sql = Path(DEMO_DIR, 'query.sql').read_text()
    result = run_query(sql)
    papers = dict(flatten_row(row) for row in result)
    predictions = run_cso_classifier_batch_mode(papers, workers=4)
    write_output(predictions, papers)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(usage='Demonstrate the CSO Classifier on some CS articles in Web of Science.')
    args = parser.parse_args()
    main()
