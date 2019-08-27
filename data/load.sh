#!/bin/bash

bq --location=us-east1 load \
    -source_format=NEWLINE_DELIMITED_JSON \
    TABLE \
    gs://cso-classifier/cset-predictions-clarivate-input*.jsonl \
    prediction-schema.json
