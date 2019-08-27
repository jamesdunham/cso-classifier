#!/bin/bash
# Create BQ table for predictions
# Reference: https://cloud.google.com/bigquery/docs/tables

bq mk \
  --table \
  --description description \
  gcp-cset-projects:gcp_cset_clarivate.cso_predictions \
  prediction-schema.json
