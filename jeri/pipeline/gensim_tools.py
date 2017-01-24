"""Some utility functions for working with gensim."""

from collections import defaultdict
import json
from gensim import corpora, models, similarities

STOPLIST = ("for", "a", "of", "the", "and", "to", "in")
LABELS = ("ORG", "AUT", "EXP", "CEL", "MED", "UNA", "SKIP")

def get_documents_from_memory(memory_file):
    with open(memory_file) as infile:
        memory = json.load(infile)
    documents_dict = {label: [] for label in LABELS}
    for entity, label in memory.items():
        documents_dict[label].append(entity)
    documents = []
    for label in LABELS:
        documents.append(" ".join(documents_dict[label]))
    return documents

def get_dictionary_corpus_from_documents(documents):
    texts = [[word for word in document.lower().split()
              if word not in STOPLIST] for document in documents]

    frequency = defaultdict(int)
    for text in texts:
        for token in text:
            frequency[token] += 1

    texts = [[token for token in text if frequency[token] > 1]
             for text in texts]

    dictionary = corpora.Dictionary(texts)
    corpus = [dictionary.doc2bow(text) for text in texts]

    return dictionary, corpus

def get_lsi_index_from_dictionary_corpus(dictionary, corpus):
    tfidf = models.TfidfModel(corpus)
    corpus_tfidf = tfidf[corpus]

    lsi = models.LsiModel(corpus_tfidf, id2word=dictionary, num_topics=2)
    index = similarities.MatrixSimilarity(lsi[corpus])

    return lsi, index

def get_similarity_scores_from_dictionary_corpus(dictionary, corpus, doc):
    lsi, index = get_lsi_index_from_dictionary_corpus(dictionary, corpus)
    vec = dictionary.doc2bow(doc.lower().split())
    sims = index[lsi[vec]]
    return sims

def get_best_guess_and_score(labels, sims):
    sims_sorted = sorted(enumerate(sims), key=lambda x: -x[1])
    i = 0
    while sims_sorted[i][0] >= len(labels):
        i += 1
    return labels[sims_sorted[i][0]], sims_sorted[i][1]
