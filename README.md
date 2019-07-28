# CSO Classifier

## Abstract

Classifying research papers according to their research topics is an important task to improve their retrievability, assist the creation of smart analytics, and support a variety of approaches for analysing and making sense of the research environment. In this repository, we present the CSO Classifier, a new unsupervised approach for automatically classifying research papers according to the [Computer Science Ontology (CSO)](https://cso.kmi.open.ac.uk), a comprehensive ontology of research areas in the field of Computer Science. The CSO Classifier takes as input the metadata associated with a research paper (title, abstract, keywords) and returns a selection of research concepts drawn from the ontology. The approach was evaluated on a gold standard of manually annotated articles yielding a significant improvement over alternative methods.

## Table of contents

<!--ts-->
* [Abstract](#abstract)
* [Table of contents](#table-of-contents)
* [About](#about)
* [Getting started](#getting-started)
  * [Installation using PIP](#installation-using-pip)
  * [Installation using Github](#installation-using-github)
* [Usage examples](#usage-examples)
  * [Classifying a single paper (SP)](#classifying-a-single-paper-sp)
  * [Classifying in batch mode (BM)](#classifying-in-batch-mode-bm)
  * [Parameters](#parameters)
* [Releases](#releases)
  * [v2.2](#v22)
  * [v2.1](#v21)
  * [v2.0](#v20)
  * [v1.0](#v10)
* [List of Files](#list-of-files)
* [Word2vec model and token-to-cso-combined file generation](#word2vec-model-and-token-to-cso-combined-file-generation)
  * [Word Embedding generation](#word-embedding-generation)
  * [token-to-cso-combined file](#token-to-cso-combined-file)
* [License](#license)
* [References](#references)
<!--te-->

## About

The CSO Classifier is a novel application that takes as input the text from abstract, title, and keywords of a research paper and outputs a list of relevant concepts from CSO. It consists of two main components: (i) the syntactic module and (ii) the semantic module. Figure 1 depicts its architecture. The syntactic module parses the input documents and identifies CSO concepts that are explicitly referred in the document. The semantic module uses part-of-speech tagging to identify promising terms and then exploits word embeddings to infer semantically related topics. Finally, the CSO Classifier combines the results of these two modules and enhances them by including relevant super-areas.

![Framework of CSO Classifier](https://github.com/angelosalatino/cso-classifier/raw/master/images/Workflow.png "Framework of CSO Classifier")
**Figure 1**: Framework of CSO Classifier

## Getting started

### Installation

1. Ensure you have [**Python 3.6**](https://www.python.org/downloads/) or above installed.
2. Install the necessary depepencies by executing the following command:```pip install -r requirements.txt```
3. Download English package for spaCy using ```python -m spacy download en_core_web_sm```

### Parameters
Beside the paper(s), the function running the CSO Classifier accepts three additional parameters: (i) **workers**, (ii) **modules**, and (iii) **enhancement**. Here we explain their usage. The workers parameters is an integer (equal or greater than 1), modules and enhancement are strings that define a particular behaviour for the classifier.

(1) The parameter *workers* defines the number of thread to run for classifying the input corpus. For instance, if workers is set to 4. There will be 4 instances of the CSO Classifier, each one receiving a chunk (equally split) of the corpus to process. Once all processes are completed, the results will be aggregated and returned. The default value for *workers* is *1*. This parameter is available only in *batch mode*.

(2) The parameter *modules* can be either "syntactic", "semantic", or "both". Using the value "syntactic", the classifier will run only the syntactic module. Using the "semantic" value, instead, the classifier will use only the semantic module. Finally, using "both", the classifier will run both syntactic and semantic modules and combine their results. The default value for *modules* is *both*.

(3) The parameter *enhancement* can be either "first", "all", or "no". This parameters controls whether the classifier will try to infer, given a topic (e.g., Linked Data), only the direct super-topics (e.g., Semantic Web) or all its super-topics (e.g., Semantic Web, WWW, Computer Science). Using "first" as value, it will infer only the direct super topics. Instead, if using "all", the classifier will infer all its super-topics. Using "no" the classifier will not perform any enhancement. The default value for *enhancement* is *first*.

| Parameter  |  Single Paper | Batch Mode |
|---|---|---|
| workers  | :x:  | :white_check_mark: |
| modules  | :white_check_mark:  | :white_check_mark: |
| enhancement  | :white_check_mark:  | :white_check_mark: |

**Table 1**: Parameters availability when using CSO Classifier


## Releases

Here we list the available releases for the CSO Classifier. These releases are available for download both from [Github](https://github.com/angelosalatino/cso-classifier/releases) and [Zenodo](10.5281/zenodo.2660819).

### v2.2
In this version (release v2.2), we (i) updated the requirements needed to run the classifier, (ii) removed all unnecessary warnings, and (iii) enabled multiprocessing. In particular, we removed all useless requirements that were installed in development mode, by cleaning the _requirements.txt_ file. 

When computing certain research papers, the classifier display warnings raised by the [kneed library](https://pypi.org/project/kneed/). Since the classifier can automatically adapt to such warnings, we decided to hide them and prevent users from being concerned about such outcome.

This version of the classifier provides improved **scalablibility** through multiprocessing. Once the number of workers is set (i.e. num_workers >= 1), each worker will be given a copy of the CSO Classifier with a chunk of the corpus to process. Then, the results will be aggregated once all processes are completed. Please be aware that this function is only available in batch mode. See section [Classifying in batch mode (BM)](#classifying-in-batch-mode-bm) for more details.

Download from:

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.3241490.svg)](https://doi.org/10.5281/zenodo.3241490)

### v2.1
This new release (version v2.1) makes the CSO Classifier more scalable. Compared to its previous version (v2.0), the classifier relies on a cached word2vec model which connects the words within the model vocabulary directly with the CSO topics. Thanks to this cache, the classifier is able to quickly retrieve all CSO topics that could be inferred by given tokens, speeding up the processing time. In addition, this cache is lighter (~64M) compared to the actual word2vec model (~366MB), which allows to save additional time at loading time.

Thanks to this improvement the CSO Classifier is around 24x faster and can be easily run on large corpus of scholarly data.

Download from:

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.2689440.svg)](https://doi.org/10.5281/zenodo.2689440)

### v2.0

> Salatino, A.A., Osborne, F., Thanapalasingam, T., Motta, E.: The CSO Classifier: Ontology-Driven Detection of Research Topics in Scholarly Articles. In: TPDL 2019: 23rd International Conference on Theory and Practice of Digital Libraries. Springer. [Read More](http://oro.open.ac.uk/62026/)

### v1.0

> Salatino, A.A., Thanapalasingam, T., Mannocci, A., Osborne, F. and Motta, E. 2018. Classifying Research Papers with the Computer Science Ontology. ISWC-P&D-Industry-BlueSky 2018 (2018). [Read more](http://oro.open.ac.uk/55908/)

## List of Files

* **CSO-Classifier.ipynb**: :page_facing_up: Python notebook for executing the classifier
* **requirements.txt**: :page_facing_up: File containing the necessary libraries to run the classifier
* **images**: :file_folder: folder containing some pictures, e.g., the workflow showed above
* **classifier**: :file_folder: Folder containing the main functionalities of the classifier
  * **classifier.py**: :page_facing_up: contains the function for running the CSO Classifier
  * **syntacticmodule.py**: :page_facing_up: functionalities that implement the syntactic module
  * **semanticmodule.py**: :page_facing_up: functionalities that implement the semantic module
  * **misc.py**: :page_facing_up: some miscellaneous functionalities
  * **models**: :file_folder: Folder containing the word2vec model and CSO
    * **cso.csv**: :page_facing_up: file containing the Computer Science Ontology in csv
    * **cso.p**: :page_facing_up: serialised file containing the Computer Science Ontology (pickled)
    * **token-to-cso-combined.json**: :page_facing_up: file containing the cached word2vec model. This json file contains a dictionary in which each token of the corpus vocabulary, has been mapped with the corresponding CSO topics. Below we explain how this file has been generated.

## Word2vec model and token-to-cso-combined file generation

In this section, we describe how we generated the word2vec model used within the CSO Classifier and what is the token-to-cso-combined file.

### Word Embedding generation

We applied the word2vec approach [[2,3]](#references) to a collection of text from the Microsoft Academic Graph (MAG)  for generating word embeddings. MAG is a scientific knowledge base and a heterogeneous graph containing scientific publication records, citation relationships, authors, institutions, journals, conferences, and fields of study. It is the largest dataset of scholarly data publicly available, and, as of December 2018, it contains more than 210 million publications.

We first downloaded titles, and abstracts of 4,654,062 English papers in the field of Computer Science. Then we pre-processed the data by replacing spaces with underscores in all n-grams matching the CSO topic labels (e.g., “digital libraries” became “digital_libraries”) and for frequent bigrams and trigrams (e.g., “highest_accuracies”, “highly_cited_journals”). These frequent n-grams were identified by analysing combinations of words that co-occur together, as suggested in [[2]](#references) and using the parameters showed in Table 2. Indeed, while it is possible to obtain the vector of a n-gram by averaging the embedding vectors of all it words, the resulting representation usually is not as good as the one obtained by considering the n-gram as a single word during the training phase.

Finally, we trained the word2vec model using the parameters provided in Table 3. The parameters were set to these values after testing several combinations.

| min-count  |  threshold |
|---|---|
| 5  | 10  |

**Table 2**: Parameters used during the collocation words analysis


| method  |  emb. size | window size | min count cutoff |
|---|---|---|---|
| skipgram  | 128  |  10 |  10 |

**Table 3**: Parameters used for training the word2vec model.


After training the model, we obtained a **gensim.models.keyedvectors.Word2VecKeyedVectors** object weighing **366MB**. You can download the model [from here](https://cso.kmi.open.ac.uk/download/model.p).

The size of the model hindered the performance of the classifier in two ways. Firstly, it required several seconds to be loaded into memory. This was partially fixed by serialising the model file (using python pickle, see version v2.0 of CSO Classifier, ~4.5 times faster). Secondly, while processing a document, the classifier needs to retrieve the top 10 similar words for all tokens, and compare them with CSO topics. In performing such operation, the model would recquire several seconds, becoming a bottleneck for the classification process.

To this end, we decided to create a cached model (**token-to-cso-combined.json**) which is a dictionary that directly connects all token available in the vocabulary of the model with the CSO topics. This strategy allows to quickly retrieve all CSO topics that can be inferred by a particular token.

### token-to-cso-combined file

To generate this file, we collected all the set of words available within the vocabulary of the model. Then iterating on each word, we retrieved its top 10 similar words from the model, and we computed their Levenshtein similarity against all CSO topics. If the similarity was above 0.7, we created a record which stored all CSO topics triggered by the initial word.


## License

[Apache 2.0](https://choosealicense.com/licenses/apache-2.0/)

## References

[1] Osborne, F., Salatino, A., Birukou, A. and Motta, E. 2016. Automatic Classification of Springer Nature Proceedings with Smart Topic Miner. The Semantic Web -- ISWC 2016. 9982 LNCS, (2016), 383–399. DOI:https://doi.org/10.1007/978-3-319-46547-0_33

[2] Mikolov, T., Chen, K., Corrado, G. and Dean, J. 2013. Efficient Estimation of Word Representations in Vector Space. (Jan. 2013).

[3] Mikolov, T., Chen, K., Corrado, G. and Dean, J. 2013. Distributed Representations of Words and Phrases and their Compositionality. Advances in neural information processing systems. 3111–3119.
