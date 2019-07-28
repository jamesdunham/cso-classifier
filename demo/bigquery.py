"""
Request query results from BigQuery.

References:
    - https://googleapis.github.io/google-cloud-python/latest/storage/buckets.html
"""
from google.cloud import bigquery

from demo.settings import DEMO_DIR

PROJECT = 'gcp-cset-projects'
QUERY_PATH = DEMO_DIR / 'query.sql'


def run_query():
    bq_client = bigquery.Client(project=PROJECT)
    # This is a SQL query for BigQuery that joins titles, abstracts, and keywords from  Web of Science
    query = QUERY_PATH.read_text()
    # The query method starts the job and doesn't block
    job = bq_client.query(query)
    # The job results method blocks while waiting for the job to complete
    result = job.result()
    papers = flatten(result)
    return papers


def flatten(result):
    papers = {}
    for row in result:
        keywords = ', '.join([kw.replace(',', '') for kw in row['keywords']])
        paper = dict(row)
        paper.update(keywords=keywords)
        papers[paper.pop('id')] = paper
    return papers
