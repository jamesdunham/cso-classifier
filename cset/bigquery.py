"""
Request query results from BigQuery.

References:
    - https://googleapis.github.io/google-cloud-python/latest/bigquery/index.html
"""
from google.cloud import bigquery

PROJECT = 'gcp-cset-projects'


def run_query(sql):
    bq_client = bigquery.Client(project=PROJECT)
    # The query method starts the job and doesn't block
    job = bq_client.query(sql)
    # The job results method blocks while waiting for the job to complete
    result = job.result()
    for row in result:
        yield row


def flatten_row(row):
    keywords = ', '.join([kw.replace(',', '') for kw in row['keywords']])
    paper = dict(row)
    paper.update(keywords=keywords)
    return paper.pop('id'), paper


def flatten(result):
    papers = {}
    for row in result:
        keywords = ', '.join([kw.replace(',', '') for kw in row.get('keywords', [])])
        paper = dict(row)
        paper.update(keywords=keywords)
        papers[paper.pop('id')] = paper
    return papers
