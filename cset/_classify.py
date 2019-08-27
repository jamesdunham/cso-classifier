import logging

from classifier.misc import load_ontology_and_chached_model

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

CSO, MODEL = load_ontology_and_chached_model()
