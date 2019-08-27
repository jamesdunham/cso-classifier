#!/bin/bash

bq extract \
    --destination_format NEWLINE_DELIMITED_JSON \
    gcp-cset-projects:gcp_cset_clarivate.computer_science_title_keyword_abstract \
    gs://cso-classifier/clarivate-input-*.jsonl
