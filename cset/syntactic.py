import re
from collections import defaultdict
from typing import List

from Levenshtein.StringMatcher import StringMatcher
from nltk import ngrams

from cset.classify import CSO
from cset.preprocess import clean_tokens

# Computing the topic stems once here instead of with each iteration offers compute gains
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
        # i indexes the same token in the text whether we're matching by unigram, bigram, or trigram
        for i, grams in enumerate(ngrams(tokens, n)):
            # if we already matched the current token to a topic, don't reprocess it
            if i in matches:
                continue
            # otherwise unsplit the ngram for matching so ('quick', 'brown') => 'quick brown'
            gram = " ".join(grams)
            try:
                # if there isn't an exact match on the first 4 characters of the ngram and a topic, move on
                topic_block = TOPIC_STEMS[gram[:4]]
            except KeyError:
                continue
            for topic in topic_block:
                # otherwise look for an inexact match
                match_ratio = StringMatcher(None, topic, gram).ratio()
                if match_ratio >= min_similarity:
                    try:
                        # if a 'primary label' exists for the current topic, use it instead of the matched topic
                        topic = CSO['primary_labels'][topic]
                    except KeyError:
                        pass
                    # note the tokens that matched the topic and how closely
                    found_topics[topic].append({'matched': gram, 'similarity': match_ratio})
                    # don't reprocess the current token
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
