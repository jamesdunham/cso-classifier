"""Flatten prediction JOSNL.

We can't load arbitrary key names like this into BQ:

  "enhanced": {
    "field programmable gate arrays (fpga)": [
      {
        "matched": 2,
        "broader of": [
          "hardware design",
          "hardware resources"
        ]
      }
    ]
  }

"""
import json
from pathlib import Path


def main():
    for prediction in Path('.').glob('cset-predictions*.jsonl'):
        output_path = prediction.with_name(f'flat-{prediction.name}')
        with prediction.open('rt') as infile:
            with output_path.open('wt') as outfile:
                for line in infile:
                    record = json.loads(line)
                    # Deduplicate and flatten 'enhanced' values
                    enhanced = {}
                    for term, matches in record['enhanced'].items():
                        for match in matches:
                            # Uniqueness is defined by term + match count + broader terms
                            key = (term, match['matched'], tuple(match['broader of']))
                            # Move the term into the 'enhanced' record as 'term'
                            enhanced[key] = {'term': term, 'matched': match['matched'], 'broader': match['broader of']}
                    # 'enhanced' is now an array of records
                    record['enhanced'] = list(enhanced.values())
                    outfile.write(json.dumps(record) + '\n')


if __name__ == '__main__':
    main()
