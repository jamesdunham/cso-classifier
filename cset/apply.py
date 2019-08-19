"""
Apply the CSO classifier to the result of a BQ query.
"""
from datetime import datetime

from cset.batch import Paper, batch_predict
from cset.bigquery import run_query, flatten_row


def fetch_papers():
    for row in run_query(
            'select id, title, keywords, abstract '
            'from `gcp-cset-projects.gcp_cset_clarivate.computer_science_title_keyword_abstract`'):
        yield flatten_row(row)


def main():
    papers = (Paper(id=k, **v) for k, v in fetch_papers())
    output_path = 'CSO Output {}.jsonl'.format(datetime.now().strftime('%Y-%m-%d %X'))
    batch_predict(papers, output_path)


if __name__ == '__main__':
    main()
