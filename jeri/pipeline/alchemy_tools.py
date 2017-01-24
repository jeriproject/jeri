"""Functions that wrap Alchemy API calls and extract useful information from the response."""

import json

from jeri.AlchemyAPI.alchemyapi import AlchemyAPI

def get_entities_to_dict(infile):
    """Returns the AlchemyAPI entities response as a dictionary."""
    api = AlchemyAPI()
    text = open(infile, 'r').read()
    response = api.entities('text', text, {
        'quotations': 1,
        'sentiment': 1,
        'showSourceText': 1,
        'knowledgeGraph:': 1,
    })
    return response

def get_entities_to_file(infile, outfile):
    """Writes the AlchemyAPI entities response to file (JSON)."""
    response = get_entities_to_dict(infile)

    with open(outfile, 'w') as output:
        json.dump(response, output)

def get_relations_to_dict(infile):
    """Returns the AlchemyAPI relations response as a dictionary."""
    api = AlchemyAPI()
    text = open(infile, 'r').read()
    response = api.relations('text', text, {
        'sentiment': 1,
        'entities': 1,
        'requireEntities': 1,
        'showSourceText:': 1,
    })
    return response

def get_relations_to_file(infile, outfile):
    """Writes the AlchemyAPI relations response to file (JSON)."""
    response = get_relations_to_dict(infile)

    with open(outfile, 'w') as output:
        json.dump(response, output)

def get_entities(response):
    """Returns all entities."""
    return response['entities']

def get_relations(response):
    """Returns all relations."""
    return response['relations']

def get_relations_by_action_lemm(response, action_lemm):
    relations = get_relations(response)
    things = []
    for relation in relations:
        if relation['action']['lemmatized'].lower() == action_lemm.lower():
            things.append(relation)
    return things

def get_entities_by_action_lemm(response_rel, action_lemm):
    relations = get_relations_by_action_lemm(response_rel, action_lemm)
    things = []
    for relation in relations:
        subject = relation['subject']
        if 'entities' in subject.keys():
            things.append(subject['entities'])
    return things
