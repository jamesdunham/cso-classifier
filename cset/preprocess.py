import spacy

from cset.model import Paper

tokenizer = spacy.load('en_core_web_sm', disable=['tagger', 'parser', 'ner'])
tagger = spacy.load('en_core_web_sm', disable=['parser', 'ner'])


def clean_tokens(paper: Paper) -> str:
    doc = tokenizer(paper.text)
    for token in doc:
        if not any((token.is_stop, token.is_punct)):
            yield token.lower_


def tag_tokens(paper: Paper) -> str:
    doc = tagger(paper.text)
    for token in doc:
        if token.tag_:
            yield token.text, token.tag_
