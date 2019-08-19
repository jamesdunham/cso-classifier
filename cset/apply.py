"""
Apply the CSO classifier to the result of a BQ query.
"""
import argparse
import logging
import sys
from datetime import datetime

from cset.batch import Paper, batch_predict
from cset.bigquery import run_query, flatten_row

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def fetch_papers():
    for row in run_query(
            'select id, title, keywords, abstract '
            'from `gcp-cset-projects.gcp_cset_clarivate.computer_science_title_keyword_abstract`'):
        yield flatten_row(row)


def main(output_path):
    papers = (Paper(id=k, **v) for k, v in fetch_papers())
    batch_predict(papers, output_path)


if __name__ == '__main__':
    logger.addHandler(logging.StreamHandler(sys.stdout))
    default_output_path = 'CSO Output {}.jsonl'.format(datetime.now().strftime('%Y-%m-%d %X'))
    parser = argparse.ArgumentParser(usage='Apply the CSO classifier to the result of a BQ query.')
    parser.add_argument('--output', default=default_output_path)
    args = parser.parse_args()
    main(args.output)
