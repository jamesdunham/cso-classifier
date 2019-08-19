"""
Run the CSO classifier in batch mode.
"""
import argparse
import concurrent.futures
import json
import logging
import sys
from dataclasses import dataclass
from datetime import datetime
from functools import partial
from typing import List

from tqdm import tqdm

from classifier import misc
from classifier.misc import climb_ontology
from classifier.semanticmodule import CSOClassifierSemantic
from classifier.syntacticmodule import CSOClassifierSyntactic
from main import load_input

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


@dataclass
class Paper:
    id: str
    title: str
    keywords: List[str]
    abstract: str = ''
    abstract_text: str = ''

    def __post_init__(self):
        if isinstance(self.keywords, str):
            self.keywords = [s.lower().strip() for s in self.keywords.split(',')]
        elif isinstance(self.keywords, list):
            self.keywords = [s.lower().strip() for s in self.keywords]
        else:
            raise TypeError('Pass keywords as a comma-delimited string or as a list')
        if not self.abstract_text:
            self.abstract = self.abstract_text


def load_classifiers():
    cso, model = misc.load_ontology_and_chached_model()
    syntactic_classifier = CSOClassifierSyntactic(cso)
    semantic_classifier = CSOClassifierSemantic(model, cso)
    return cso, syntactic_classifier, semantic_classifier


def predict(paper, cso, syntactic_classifier, semantic_classifier):
    syntactic_classifier.set_paper(paper)
    semantic_classifier.set_paper(paper)
    prediction = dict(syntactic=syntactic_classifier.classify_syntactic(),
                      semantic=semantic_classifier.classify_semantic())
    prediction['enhanced'] = climb_ontology(cso, set(prediction['syntactic']).union(prediction['semantic']), 'all')
    return prediction


def batch_predict(papers, output_path, workers=4):
    # Load the classifiers only once
    cso, syntactic_classifier, semantic_classifier = load_classifiers()
    _predict = partial(predict, cso=cso, syntactic_classifier=syntactic_classifier,
                       semantic_classifier=semantic_classifier)
    with open(output_path, 'at') as output:
        with concurrent.futures.ProcessPoolExecutor(max_workers=workers) as executor:
            with tqdm() as pbar:
                # Map futures to papers (this doesn't block)
                future_predictions = {executor.submit(_predict, paper.__dict__): paper.id for paper in papers}
                # Generate predictions in order of completion
                for future in concurrent.futures.as_completed(future_predictions):
                    # Recover the input paper
                    paper_id = future_predictions[future]
                    try:
                        prediction = {paper_id: future.result()}
                        output.write(json.dumps(prediction) + '\n')
                    except Exception as e:
                        logger.error('Exception processing {}: {}'.format(paper_id, e))
                    else:
                        pbar.update()


if __name__ == '__main__':
    logger.addHandler(logging.StreamHandler(sys.stdout))

    parser = argparse.ArgumentParser(usage='Apply the CSO Classifier to a batch of inputs.')
    parser.add_argument('--file', type=argparse.FileType('rt'), default=None)
    parser.add_argument('--output', default=None)
    args = parser.parse_args()

    # Read inputs
    if args.file is None:
        logger.info('Reading from demo-inputs.json by default')
        inputs = load_input()
    else:
        logger.info('Reading from {}'.format(args.file))
        inputs = json.load(args.file)

    # Set output path
    if args.output is None:
        output_path = 'CSO Output {}.jsonl'.format(datetime.now().strftime('%Y-%m-%d %X'))
    else:
        output_path = args.output
    logger.info('Writing to {}'.format(output_path))

    # Parse inputs
    papers = [Paper(id=k, **v) for k, v in inputs.items()]

    # Start prediction
    batch_predict(papers, output_path)
