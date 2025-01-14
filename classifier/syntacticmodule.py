#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Nov 22 09:09:10 2018

@author: angelosalatino
"""
import logging
import os
from collections import defaultdict

import Levenshtein.StringMatcher as ls
from nltk import ngrams
from nltk.corpus import stopwords
from nltk.tokenize import RegexpTokenizer
from nltk.tokenize import word_tokenize

logger = logging.getLogger(__name__)
log_level = os.getenv('LOG_LEVEL', 'DEBUG')
logger.setLevel(getattr(logging, log_level))


class CSOClassifierSyntactic:
    """ An simple abstraction layer for using CSO classifier """

    def __init__(self, cso=None, paper=None):
        """Function that initialises an object of class CSOClassifierSyntactic and all its members.

        Args:
            cso (dictionary): Computer Science Ontology
            paper (dictionary): paper{"title":"...","abstract":"...","keywords":"..."} the paper.

        """
        # Initialise variables to store CSO data - loads into memory 
        if paper is None:
            self.paper = {}
        else:
            self.set_paper(paper)
        if cso is None:
            cso = {}
        self.cso = cso
        self.min_similarity = 0.94

    def set_paper(self, paper):
        """Function that initializes the paper variable in the class.

        Args:
            paper (either string or dictionary): The paper to analyse. It can be a full string in which the content
            is already merged or a dictionary  {"title": "","abstract": "","keywords": ""}.

        """
        if isinstance(paper, str):
            self.paper = paper.strip()
        elif isinstance(paper, dict):
            # Handle keywords passed as a list
            if isinstance(paper.get('keywords'), list):
                paper['keywords'] = ', '.join(paper['keywords'])
            expected_fields = ['title', 'abstract', 'keywords']
            field_text = (paper.get(field) for field in expected_fields)
            self.paper = '. '.join((text for text in field_text if text))
        else:
            raise TypeError('Pass paper as a string or dict that maps "title", "abstract", and "keywords" to strings')
        assert self.paper, 'No paper text found'

    def set_min__similarity(self, msm):
        """Function that sets a different value for the similarity.

        Args:
            msm (integer): similairity value.
        """
        self.min_similarity = msm

    def classify_syntactic(self):
        """Function that classifies a single paper. If you have a collection of papers, 
            you must call this function for each paper and organise the result.
           Initially, it cleans the paper file, removing stopwords (English ones) and punctuation.
           Then it extracts n-grams (1,2,3) and with a Levenshtein it check the similarity for each of
           them with the topics in the ontology.
           Next, it climbs the ontology, by selecting either the first broader topic or the whole set of
           broader topics until root is reached.

        Args:


        Returns:
            found_topics (dictionary): containing the found topics with their similarity and the n-gram analysed.
        """

        # pre-processing
        paper = self.paper.lower()
        tokenizer = RegexpTokenizer(r'[\w\-\(\)]*')
        tokens = tokenizer.tokenize(paper)
        filtered_words = [w for w in tokens if w not in stopwords.words('english')]
        paper = " ".join(filtered_words)

        # analysing similarity with terms in the ontology
        extracted_topics = self.statistic_similarity(paper, self.min_similarity)
        topics = self.strip_explanation(extracted_topics)

        return topics

    def statistic_similarity(self, paper, min_similarity):
        """Function that splits the paper text in n-grams (unigrams,bigrams,trigrams)
        and with a Levenshtein it check the similarity for each of them with the topics in the ontology.

        Args:
            paper (string): The paper to analyse. At this stage it is a string.
            min_similarity (integer): minimum Levenshtein similarity between the n-gram and the topics within the CSO. 

        Returns:
            found_topics (dictionary): containing the found topics with their similarity and the n-gram analysed.
        """

        # analysing grams
        found_topics = defaultdict(list)
        matches = set()
        tokens = word_tokenize(paper, preserve_line=True)
        # TODO: this is constant; factor out
        topic_stems = defaultdict(list)
        for k in self.cso['topics'].keys():
            topic_stems[k[:4]].append(k)

        for n in range(3, 0, -1):
            for i, grams in enumerate(ngrams(tokens, n)):
                if i in matches:
                    continue
                gram = " ".join(grams)
                try:
                    topic_block = topic_stems[gram[:4]]
                except KeyError:
                    continue
                for topic in topic_block:
                    m = ls.StringMatcher(None, topic, gram).ratio()
                    if m >= min_similarity:
                        topic = self.get_primary_label(topic, self.cso['primary_labels'])
                        found_topics[topic].append({'matched': gram, 'similarity': m})
                        matches.add(i)

        # idx = 0
        # trigrams = ngrams(word_tokenize(paper, preserve_line=True), 3)
        # matched_trigrams = []
        # for grams in trigrams:
        #     idx += 1
        #     gram = " ".join(grams)
        #     topic_block = [key for key, _ in self.cso['topics'].items() if key.startswith(gram[:4])]
        #     for topic in topic_block:
        #         m = ls.StringMatcher(None, topic, gram).ratio()
        #         if m >= min_similarity:
        #             topic = self.get_primary_label(topic, self.cso['primary_labels'])
        #             if topic in found_topics:
        #                 found_topics[topic].append({'matched': gram, 'similarity': m})
        #             else:
        #                 found_topics[topic] = [{'matched': gram, 'similarity': m}]
        #             matched_trigrams.append(idx)
        #
        # idx = 0
        # bigrams = ngrams(word_tokenize(paper, preserve_line=True), 2)
        # matched_bigrams = []
        # for grams in bigrams:
        #     idx += 1
        #     if (idx not in matched_trigrams) and ((idx - 1) not in matched_trigrams):
        #         gram = " ".join(grams)
        #         topic_block = [key for key, _ in self.cso['topics'].items() if key.startswith(gram[:4])]
        #         for topic in topic_block:
        #             m = ls.StringMatcher(None, topic, gram).ratio()
        #             if m >= min_similarity:
        #                 topic = self.get_primary_label(topic, self.cso['primary_labels'])
        #                 if topic in found_topics:
        #                     found_topics[topic].append({'matched': gram, 'similarity': m})
        #                 else:
        #                     found_topics[topic] = [{'matched': gram, 'similarity': m}]
        #                 matched_bigrams.append(idx)
        #
        # idx = 0
        # unigrams = ngrams(word_tokenize(paper, preserve_line=True), 1)
        # for grams in unigrams:
        #     idx += 1
        #     if (idx not in matched_trigrams) and ((idx - 1) not in matched_trigrams) and (
        #             idx not in matched_bigrams) and ((idx - 1) not in matched_bigrams) and (
        #             (idx - 1) not in matched_bigrams):
        #         gram = " ".join(grams)
        #         topic_block = [key for key, _ in self.cso['topics'].items() if key.startswith(gram[:4])]
        #         for topic in topic_block:
        #             m = ls.StringMatcher(None, topic, gram).ratio()
        #             if m >= min_similarity:
        #                 topic = self.get_primary_label(topic, self.cso['primary_labels'])
        #                 if topic in found_topics:
        #                     found_topics[topic].append({'matched': gram, 'similarity': m})
        #                 else:
        #                     found_topics[topic] = [{'matched': gram, 'similarity': m}]

        return found_topics

    def strip_explanation(self, found_topics):
        """Function that removes statistical values from the dictionary containing the found topics.
            It returns only the topics. It removes the same as, picking the longest string in alphabetical order.

        Args:
            found_topics (dictionary): It contains the topics found with string similarity.

        Returns:
            topics (array): array containing the list of topics.
        """

        topics = list(set(found_topics.keys()))  # Takes only the keys

        return topics

    def get_primary_label(self, topic, primary_labels):
        """Function that returns the primary (preferred) label for a topic. If this topic belongs to 
        a cluster.

        Args:
            topic (string): Topic to analyse.
            primary_labels (dictionary): It contains the primary labels of all the topics belonging to clusters.

        Returns:
            topic (string): primary label of the analysed topic.
        """

        try:
            topic = primary_labels[topic]
        except KeyError:
            pass

        return topic
