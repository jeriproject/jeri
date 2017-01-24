"""Some utility functions for working with the NLTK library."""

import nltk

def get_tokens(text):
    return nltk.word_tokenize(text)

def get_postagged_tokens(text):
    tokens = get_tokens(text)
    #tagger = nltk.tag.StanfordPOSTagger('classifiers/english.all.3class.distsim.crf.ser.gz')
    #return tagger.tag(tokens)
    return nltk.tag.pos_tag(tokens)

def get_nertagged_tokens(text):
    tokens = get_tokens(text)
    tagger = nltk.tag.StanfordNERTagger('classifiers/english.all.3class.distsim.crf.ser.gz')
    return tagger.tag(tokens)

def get_chunked_proper_nouns(text):
    """Extracts all chunked proper nouns."""
    chunked_proper_nouns = []

    sentence_tokenizer = nltk.data.load("tokenizers/punkt/english.pickle")

    sentences = sentence_tokenizer.tokenize(text)
    for sentence in sentences:
        tokens = nltk.tokenize.word_tokenize(sentence)
        tagged_tokens = nltk.tag.pos_tag(tokens)
        current = []

        for token, pos in tagged_tokens:
            if pos == 'NNP':
                current.append(token)
                continue

            if len(current) > 0:
                chunked_proper_nouns.append(current)
                current = []

        if len(current) > 0:
            chunked_proper_nouns.append(current)

    return chunked_proper_nouns
