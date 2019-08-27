import re
from collections import defaultdict
from typing import List

from Levenshtein.StringMatcher import StringMatcher
from nltk import ngrams, Tree

from cset._classify import CSO
from cset._preprocess import clean_tokens

TOPIC_STEMS = defaultdict(list)
for k in CSO['topics'].keys():
    TOPIC_STEMS[k[:4]].append(k)


def classify_syntactic(paper, min_similarity=.96):
    tokens = clean_tokens(paper)
    topics = match_ngrams(list(tokens), min_similarity=min_similarity)
    topics = list(set(topics.keys()))
    return topics


def match_ngrams(tokens: List, min_similarity=.96):
    found_topics = defaultdict(list)
    matches = set()
    for n in range(3, 0, -1):
        for i, grams in enumerate(ngrams(tokens, n)):
            if i in matches:
                continue
            gram = " ".join(grams)
            try:
                topic_block = TOPIC_STEMS[gram[:4]]
            except KeyError:
                continue
            for topic in topic_block:
                match_ratio = StringMatcher(None, topic, gram).ratio()
                if match_ratio >= min_similarity:
                    try:
                        topic = CSO['primary_labels'][topic]
                    except KeyError:
                        pass
                    found_topics[topic].append({'matched': gram, 'similarity': match_ratio})
                    matches.add(i)
    return found_topics


def collapse_tree(node):
    concept = ''
    for text, tag in node.leaves():
        text = re.sub('[\=\,\…\’\'\+\-\–\“\”\"\/\‘\[\]\®\™\%]', ' ', text)
        text = re.sub('\.$|^\.', '', text)
        text = text.lower().strip()
        concept += ' ' + text
    concept = re.sub('\.+', '.', concept)
    concept = re.sub('\s+', ' ', concept)
    return concept


def extract_phrases(parse):
    for node in parse:
        if isinstance(node, Tree) and node.label() == 'DBW_CONCEPT':
            # The tree matches the grammar
            yield collapse_tree(node)
