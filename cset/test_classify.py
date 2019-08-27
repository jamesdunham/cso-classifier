from cset._syntactic import classify_syntactic
from cset._semantic import classify_semantic
from cset.model import Paper
from cset._preprocess import clean_tokens


def test_classify_semantic():
    paper = Paper(title='The quick brown fox jumped over the lazy neural network.')
    topics = classify_semantic(paper)
    assert topics == ['neural networks', 'feedforward neural networks', 'lazy evaluation', 'network architecture',
                      'network components']


def test_classify_syntactic():
    paper = Paper(title='The quick brown fox jumped over the lazy neural network.')
    topics = classify_syntactic(paper)
    assert topics == ['neural networks']


def test_clean_tokens():
    paper = Paper(title='The quick brown fox jumped over the lazy dog.')
    clean_text = ' '.join(clean_tokens(paper))
    assert clean_text == 'quick brown fox jumped lazy dog'