"""
Demonstrate the CSO Classifier on some CS articles in Web of Science.

We fetch a set of paper titles, abstracts and keywords from BigQuery, run the CSO Classifier over them, and write the
result to the `demo` directory as `demo-predictions.json`.
"""
import argparse
import json
import logging
import sys
from pathlib import Path

from tqdm import tqdm

from classifier import misc
from classifier.misc import climb_ontology
from classifier.semanticmodule import CSOClassifierSemantic
from classifier.syntacticmodule import CSOClassifierSyntactic
from cset._semantic import classify_semantic
from cset._syntactic import classify_syntactic
from cset.model import Paper

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def load_classifiers():
    cso, model = misc.load_ontology_and_chached_model()
    syntactic_classifier = CSOClassifierSyntactic(cso)
    semantic_classifier = CSOClassifierSemantic(model, cso)
    return cso, syntactic_classifier, semantic_classifier


def load_cso():
    cso, model = misc.load_ontology_and_chached_model()
    return cso


def predict(paper, cso, syntactic_classifier, semantic_classifier):
    syntactic_classifier.set_paper(paper)
    semantic_classifier.set_paper(paper)
    prediction = dict(syntactic=syntactic_classifier.classify_syntactic(),
                      semantic=semantic_classifier.classify_semantic())
    prediction['enhanced'] = climb_ontology(cso, set(prediction['syntactic']).union(prediction['semantic']), 'all')
    return prediction


def predict_cset(paper: Paper, cso):
    syntactic = classify_syntactic(paper)
    semantic = classify_semantic(paper)
    enhanced = climb_ontology(cso, set(syntactic).union(semantic), 'all')
    return dict(syntactic=syntactic, semantic=semantic, enhanced=enhanced)


def classify_cset(output_prefix='cset-predictions') -> None:
    """Run the CSO Classifier on CS articles from Web of Science."""
    cso = load_cso()
    data_dir = Path(__file__).parent / 'data'
    for path in data_dir.glob('*.jsonl'):
        records = (json.loads(line) for line in path.open('rt'))
        try:
            papers = {record['id']: Paper(title=record.get('title'), keywords=record.get('keywords'),
                                          abstract=record.get('abstract'))
                      for record in records}
        except KeyError as e:
            logger.error(f'KeyError reading {path}: {e}')
            continue
        output_path = path.with_name('{}-{}'.format(output_prefix, path.name))
        if output_path.exists():
            logger.info(f'Skipping existing output {output_path}')
            continue
        with output_path.open('wt') as f:
            for paper_id, paper in tqdm(papers.items()):
                prediction = predict_cset(paper, cso)
                prediction.update({'id': paper_id})
                f.write(json.dumps(prediction) + '\n')


if __name__ == '__main__':
    logger.addHandler(logging.StreamHandler(sys.stdout))
    parser = argparse.ArgumentParser(usage='Run the CSO Classifier over CS articles from Web of Science.')
    args = parser.parse_args()
    classify_cset()
