## CSET demo

This demo fetches a set of CS paper titles, abstracts, and keywords from Web of Science BigQuery tables, and runs the CSO Classifier over them.

For documentation of the CSO Classifier by its authors, see the [original repo](https://github.com/angelosalatino/cso-classifier).

## Getting started

- Clone this repo
- `pip install -r requirements.txt` (Python >= 3.6)
- `python -m spacy download en_core_web_sm` (for tokenization and stop words)
- Download a keyfile for a [service account](https://console.cloud.google.com/iam-admin/serviceaccounts/details/108948885901935517907?organizationId=266927719261&project=gcp-cset-projects) with BigQuery access into the project root
- Set the `GOOGLE_APPLICATION_CREDENTIALS` environment variable to the path of that keyfile, which will look like `"GCP-CSET Projects-b314d1aa5d86.json"`

## Use

- Run `0-extract-inputs-from-bigquery.sh` to copy Web of Science records in BigQuery to a Cloud Storage bucket
- Run `1-copy-inputs-from-storage.sh` to copy the bucket's contents to the disk (see "Input" section below)
- Run `python main.py` (e.g., `GOOGLE_APPLICATION_CREDENTIALS='gcp-cset-projects-b314d1aa5d86.json' python main.py`) to write predictions to the disk (see "Output" section below)
- Run `2-reshape-predictions.py` to reshape the predictions for loading back into BigQuery (see "Reshaped output for BigQuery" below)
- Run `3-copy-predictions-to-storage.sh` to copy the reshaped predictions to the bucket
- Run `4-create-bigquery-table.sh` to create a BigQuery table for the predictions
- Run `5-load-predictions-into-bigquery.sh` to insert the predictions into the new table

## Input

The classifier will operate on inputs `.data/*.jsonl` by default, and for each write `.data/cset-predictions-*.jsonl`.

Lines in the input file look like this, where each field is a string:
 
```JSON
{"id": "{unique id}", "title": "{title}", "keywords": "{keywords}", "abstract_text": "{abstract}" }
``` 

## Output

A single line in the output file (reformatted for exposition) looks like this:

```JSON
{
  "syntactic": [
    "flight test",
    "computer hardware"
  ],
  "semantic": [
    "flight test",
    "computer hardware",
    "hardware components",
    "hardware design",
    "hardware resources"
  ],
  "enhanced": {
    "field programmable gate arrays (fpga)": [
      {
        "matched": 2,
        "broader of": [
          "hardware design",
          "hardware resources"
        ]
      }
    ],
    "flight control systems": [
      {
        "matched": 1,
        "broader of": [
          "flight test"
        ]
      }
    ],
    "computer science": [
      {
        "matched": 4,
        "broader of": [
          "computer hardware",
          "hardware",
          "computer system",
          "computer systems"
        ]
      }
    ],
    "computer hardware": [
      {
        "matched": 8,
        "broader of": [
          "hardware components",
          "fpga",
          "field programmable gate arrays",
          "field-programmable gate arrays",
          "field-programmable gate array (fpga)",
          "field programmable gate array (fpga)",
          "field programmable gate arrays (fpga)",
          "field programmable gate array"
        ]
      }
    ],
    "embedded systems": [
      {
        "matched": 1,
        "broader of": [
          "hardware components"
        ]
      }
    ],
    "control systems": [
      {
        "matched": 2,
        "broader of": [
          "flight control systems",
          "flight control system"
        ]
      }
    ],
    "computer systems": [
      {
        "matched": 4,
        "broader of": [
          "embedded system",
          "embedded systems",
          "control systems",
          "control system"
        ]
      }
    ]
  },
  "id": "WOS:000272834900082"
}
```

## Reshaped output for BigQuery

We can't use arbitrary keys in BigQuery records, so before loading the predictions, we flatten `enhanced` so that each array element is an object with a `term` key.
See `prediction-schema.json` for the BigQuery schema.
The same example as above, reshaped for BigQuery (and intended for readability):

```JSON
{
  "syntactic": [
    "flight test",
    "computer hardware"
  ],
  "semantic": [
    "flight test",
    "computer hardware",
    "hardware components",
    "hardware design",
    "hardware resources"
  ],
  "enhanced": [
    {
      "term": "field programmable gate arrays (fpga)",
      "matched": 2,
      "broader": [
        "hardware design",
        "hardware resources"
      ]
    },
    {
      "term": "flight control systems",
      "matched": 1,
      "broader": [
        "flight test"
      ]
    },
    {
      "term": "computer science",
      "matched": 4,
      "broader": [
        "computer hardware",
        "hardware",
        "computer system",
        "computer systems"
      ]
    },
    {
      "term": "computer hardware",
      "matched": 8,
      "broader": [
        "hardware components",
        "fpga",
        "field programmable gate arrays",
        "field-programmable gate arrays",
        "field-programmable gate array (fpga)",
        "field programmable gate array (fpga)",
        "field programmable gate arrays (fpga)",
        "field programmable gate array"
      ]
    },
    {
      "term": "embedded systems",
      "matched": 1,
      "broader": [
        "hardware components"
      ]
    },
    {
      "term": "control systems",
      "matched": 2,
      "broader": [
        "flight control systems",
        "flight control system"
      ]
    },
    {
      "term": "computer systems",
      "matched": 4,
      "broader": [
        "embedded system",
        "embedded systems",
        "control systems",
        "control system"
      ]
    }
  ],
  "id": "WOS:000272834900082"
}
```