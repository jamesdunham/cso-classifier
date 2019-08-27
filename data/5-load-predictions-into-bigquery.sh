#!/bin/bash

bq load \
   --source_format=NEWLINE_DELIMITED_JSON \
    gcp-cset-projects:gcp_cset_clarivate.cso_predictions \
    gs://cso-classifier/flat-cset-predictions-clarivate-input*.jsonl \
    prediction-schema.json
