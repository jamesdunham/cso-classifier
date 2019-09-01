import warnings

from kneed import KneeLocator
from nltk import everygrams, RegexpParser

from cset.classify import CSO, MODEL
from cset.preprocess import tag_tokens

# This is a POS regex pattern for some number of nouns, possibly preceded by some number of adjectives
GRAMMAR = "DBW_CONCEPT: {<JJ.*>*<NN.*>+}"


def classify_semantic(paper, min_similarity=.96):
    # Find adjective-noun or noun spans: JJ.* matches JJ, JJR, and JJS; NN.* matches NN, NNP, NNS
    pos_tags = tag_tokens(paper)
    grammar_parser = RegexpParser(GRAMMAR)
    # RegexpParser.parse returns a parse Tree
    parse = grammar_parser.parse(list(pos_tags))
    phrases = list(extract_phrases(parse))
    topics, topic_ngrams = ngrams_to_topics(phrases, min_similarity=min_similarity)
    return rank_topics(topics)


def match_ngram(ngram, merge=True):
    matches = []
    if len(ngram) > 1 and merge:
        temp_list_of_matches = {}
        list_of_merged_topics = {}
        for token in ngram:
            if token in MODEL:
                token_topics = MODEL[token]
                for topic_item in token_topics:
                    temp_list_of_matches[topic_item["topic"]] = topic_item
                    try:
                        list_of_merged_topics[topic_item["topic"]] += 1
                    except KeyError:
                        list_of_merged_topics[topic_item["topic"]] = 1
        for topic_x, count in list_of_merged_topics.items():
            if count >= len(ngram):
                matches.append(temp_list_of_matches[topic_x])
    return matches


def ngrams_to_topics(phrases, merge=True, min_similarity=.96):
    # Core analysis: find matches
    found_topics = {}
    successful_grams = {}
    for concept in phrases:
        for ngram in everygrams(concept.split(), 1, 3):
            # TODO: pick between 'phrase' and 'concept' terminology
            concept = "_".join(ngram)
            if concept in MODEL:
                # there's an exact match for the '_'-concatenated ngram in the ontology
                matches = MODEL[concept]
            else:
                # we'll instead search for ontology elements proximate in vector space
                matches = match_ngram(ngram, merge=merge)
            for match in matches:
                topic = match["topic"]
                sim_t = match["sim_t"]
                wet = match["wet"]
                sim_w = match["sim_w"]
                if sim_t >= min_similarity and topic in CSO["topics_wu"]:
                    if topic in found_topics:
                        # tracking this match
                        found_topics[topic]["times"] += 1
                        found_topics[topic]["gram_similarity"].append(sim_w)
                        # tracking the matched gram
                        if concept in found_topics[topic]["grams"]:
                            found_topics[topic]["grams"][concept] += 1
                        else:
                            found_topics[topic]["grams"][concept] = 1
                        # tracking the most similar gram to the topic
                        if sim_t > found_topics[topic]["embedding_similarity"]:
                            found_topics[topic]["embedding_similarity"] = sim_t
                            found_topics[topic]["embedding_matched"] = wet
                    else:
                        # creating new topic in the result set
                        found_topics[topic] = {'grams': {concept: 1},
                                               'embedding_matched': wet,
                                               'embedding_similarity': sim_t,
                                               'gram_similarity': [sim_w],
                                               'times': 1,
                                               'topic': topic}
                    if sim_w == 1:
                        found_topics[topic]["syntactic"] = True
                    # reporting successful grams: it is the inverse of found_topics["topic"]["grams"]
                    if concept in successful_grams:
                        successful_grams[concept].append(topic)
                    else:
                        successful_grams[concept] = [topic]
    return found_topics, successful_grams


def rank_topics(topics):
    max_value = 0
    scores = []
    for tp, topic in topics.items():
        topic["score"] = topic["times"] * len(topic['grams'].keys())
        scores.append(topic["score"])
        if topic["score"] > max_value:
            max_value = topic["score"]
    for tp, topic in topics.items():
        if "syntactic" in topic:
            topic["score"] = max_value
    # Selection of unique topics
    unique_topics = {}
    for tp, topic in topics.items():
        prim_label = CSO["primary_labels_wu"].get(tp, tp)
        if prim_label == 'network_structures':
            print('Here I found you:', tp)
        if prim_label in unique_topics:
            if unique_topics[prim_label] < topic["score"]:
                unique_topics[prim_label] = topic["score"]
        else:
            unique_topics[prim_label] = topic["score"]
    # ranking topics by their score. High-scored topics go on top
    sorted_topics = sorted(unique_topics.items(), key=lambda v: v[1], reverse=True)
    vals = []
    for tp in sorted_topics:
        # in 0, there is the topic, in 1 there is the info
        vals.append(tp[1])
    # suppressing some warnings that can be raised by the kneed library
    warnings.filterwarnings("ignore")
    try:
        x = range(1, len(vals) + 1)
        knee_locator = KneeLocator(x, vals, direction='decreasing')
        if knee_locator.knee is None:
            # print("I performed a different identification of knee")
            knee_locator = KneeLocator(x, vals, curve='convex', direction='decreasing')
    except ValueError:
        pass
    # Prune
    try:
        knee = int(knee_locator.knee)
    except TypeError:
        knee = 0
    except UnboundLocalError:
        knee = 0

    if knee > 5:
        try:
            knee += 0
        except TypeError:
            print("ERROR: ", knee_locator.knee, " ", knee, " ", len(sorted_topics))
    else:
        try:
            if sorted_topics[0][1] == sorted_topics[4][1]:
                top = sorted_topics[0][1]
                test_topics = [item[1] for item in sorted_topics if item[1] == top]
                knee = len(test_topics)
            else:
                knee = 5
        except IndexError:
            knee = len(sorted_topics)

    final_topics = [CSO["topics_wu"][sorted_topics[i][0]] for i in range(0, knee)]
    return final_topics


def extract_phrases(parse: Tree):
    for node in parse:
        if isinstance(node, Tree) and node.label() == 'DBW_CONCEPT':
            # The tree matches the grammar
            yield collapse_tree(node)
