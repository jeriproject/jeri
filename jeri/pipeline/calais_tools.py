"""Functions that wrap OpenCalais API calls and extract useful information from the response."""

import json
import requests

from jeri.pipeline.calais_api_key import API_KEY

CALAIS_URL = 'https://api.thomsonreuters.com/permid/calais'
HEADERS = {'X-AG-Access-Token': API_KEY, 'Content-Type': 'text/raw',
           'outputformat': 'application/json'}
TIMEOUT = 80

#def get_calais_to_dict(text):
#    """Returns the OpenCalais response as a dictionary."""
#    files = {'file': text}
#    response = requests.post(CALAIS_URL, files=files, headers=HEADERS,
#                             timeout=TIMEOUT)
#    response_text = response.text
#    response_dict = json.loads(response_text)
#    return response_dict

def get_calais_to_file(text, outfile):
    """Writes the OpenCalais (JSON) response to file."""
    files = {'file': text}
    response = requests.post(CALAIS_URL, files=files, headers=HEADERS,
                             timeout=TIMEOUT)
    response_text = response.text.encode('utf-8')
    with open(outfile, 'w') as output:
        output.write(response_text)

def get_entities(response):
    """Returns all entities."""
    entities = []
    for elem in response.values():
        if '_typeGroup' in elem.keys():
            if elem['_typeGroup'] == 'entities':
                entities.append(elem)
    return entities

def get_entities_by_field(response, field, value):
    """Returns all entities with the given value for the given field."""
    entities = get_entities(response)
    things = []
    for entity in entities:
        if field in entity.keys() and value.lower() in entity[field].lower():
            things.append(entity)
    return things

def get_entities_by_type(response, ttype):
    """Returns all entities of the given type."""
    return get_entities_by_field(response, '_type', ttype)

def get_entities_by_persontype(response, persontype):
    """Returns all entities of the given persontype."""
    return get_entities_by_field(response, 'persontype', persontype)

def get_entities_by_organizationtype(response, organizationtype):
    """Returns all entities of the given organizationtype."""
    return get_entities_by_field(response, 'organizationtype', organizationtype)

def get_relations(response):
    """Returns all relations."""
    relations = []
    for elem in response.values():
        if '_typeGroup' in elem.keys():
            if elem['_typeGroup'] == 'relations':
                relations.append(elem)
    return relations

def get_relations_by_field(response, field, value):
    """Returns all relations with the given value for the given field."""
    relations = get_relations(response)
    things = []
    for relation in relations:
        if field in relation.keys() and value.lower() in relation[field].lower():
            things.append(relation)
    return things

def get_relations_by_type(response, ttype):
    """Returns all relations of the given type."""
    return get_relations_by_field(response, '_type', ttype)

def get_positions(response):
    """Returns all positions."""
    relations = get_relations(response)
    positions = []
    for relation in relations:
        if 'position' in relation.keys():
            positions.append(relation['position'])
    return positions

def get_relations_by_careertype(response, careertype):
    return get_relations_by_field(response, 'careertype', careertype)

def get_entity_instance_count(entity):
    """Returns the number of times an entity is detected."""
    return len(entity['instances'])

def get_quotation_speaker(response, quotation):
    """Returns the speaker of the given quotation."""
    speaker = response[quotation['speaker']]
    return speaker['name']

def get_career_person(response, career):
    """Returns the person of the given career."""
    person = response[career['person']]
    return person['name']

def get_company_resolutions(company):
    """Returns all resolutions of the given company."""
    res_names = ""
    if 'resolutions' in company:
        for res in company['resolutions']:
            res_names += res['name'] + ", "
    return res_names
