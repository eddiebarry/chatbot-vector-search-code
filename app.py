"""
Web application to retrieve the chit-chat reply to the closest question to the
query together with the uncertainty|confidence score of the match.
"""
from gevent import monkey
monkey.patch_all() # we need to patch very early

import logging
import sys
import os
import json
import pickle
import requests
from datetime import datetime

import flask
from flask import request, jsonify
from flask_caching import Cache

# from demo import populate_questions
from preprocessing import preprocess
from sentence_transformers import SentenceTransformer, util


logging.basicConfig(
    stream=sys.stdout, 
    level=logging.DEBUG,format='%(asctime)s %(levelname)-8s %(funcName)s %(message)s',
    datefmt="%Y-%m-%dT%H:%M:%S%z")

# SETUP
app = flask.Flask(__name__)
app.config['model'] = SentenceTransformer('/app/vector/paraphrase-MiniLM-L6-v2')
temp_data = app.config['model'].encode("The meaning of life is 42")
logging.info('model loaded')

app.config['cache'] = Cache(
    app, 
    config={
            'CACHE_TYPE': 'redis', 
            'CACHE_REDIS_URL': 'redis://:'\
                + os.getenv('REDIS_PASSWORD') + "@" \
                + os.getenv('REDIS_HOST')+ ':6379',
        }
)

app.config['vector'] = {}
app.config['data'] = {}

LOGGING_URL = 'http://'+os.getenv('LOG_HOST')+":8000/logs/"
VERSION_URL = os.getenv('VERSION_HOST')

@app.route('/get-closest', methods=['GET'])
def get_closest():
    """
    Retrieve the chit-chat reply to the closest question to the query together
    with the uncertainty|confidence score of the question closeness.
    """
    request_json = json.loads(request.data, strict=False)
    
    must = ['query']
    for key in must:
        if key not in request_json.keys():
            return jsonify({"message": "request does not contain "+key})

    if 'top_k' in request_json.keys():
        top_k=int(request_json['top_k'])
    else:
        top_k=5

    query = preprocess(request_json['query'])

    # check if available
    index_key = "qa_index"
    if index_key not in app.config['vector'].keys():
        app.config['vector'][index_key] = get_cached_vector(index_key)
        app.config['data'][index_key] = get_cached_data(index_key)
        
    if app.config['vector'][index_key] is None:
        app.config['vector'].pop(index_key)
        app.config['data'].pop(index_key)
        return jsonify({"message": "index does not exist"})

    # encode and search
    data = app.config['data'][index_key]
    search_vector = app.config['model'].encode(query)
    full_vector = app.config['vector'][index_key]
    raw_preds = util.semantic_search(search_vector, full_vector, top_k=top_k)[0]

    scoreDocs = [ [ (pred['score']+1.0)/2.0, data[pred['corpus_id']] ] for pred in raw_preds]
    # return score docs
    response = {
        'score_docs' : scoreDocs
    }
    logging.info(response)
    return jsonify(response)

@app.route('/get-chitchat', methods=['GET'])
def get_chitchat():
    """
    Retrieve the chit-chat reply to the closest question to the query together
    with the uncertainty|confidence score of the question closeness.
    """
    request_json = json.loads(request.data, strict=False)
    
    must = ['query']
    for key in must:
        if key not in request_json.keys():
            return jsonify({"message": "request does not contain "+key})

    query = preprocess(request_json['query'])

    # check if available
    index_key = "qa_index"

    if index_key not in app.config['vector'].keys():
        logging.info("pulling data from cache")
        app.config['vector'][index_key] = get_cached_vector(index_key)
        app.config['data'][index_key] = get_cached_data(index_key)
        
    if app.config['vector'][index_key] is None:
        app.config['vector'].pop(index_key)
        app.config['data'].pop(index_key)
        return jsonify({"message": "index does not exist"})

    # encode and search
    data = app.config['data'][index_key]
    search_vector = app.config['model'].encode(query)
    full_vector = app.config['vector'][index_key]
    raw_pred = util.semantic_search(search_vector, full_vector, top_k=1)[0][0]


    response = {
        "chitchat_question": data[ raw_pred['corpus_id'] ] ['question'],
        "chitchat_answer": data[ raw_pred['corpus_id'] ] ['answer'],
        "confidence": (raw_pred['score']+1.0)/2.0,
    }
    
    if response['confidence'] < 0.8:
        logging.info("sending missed query to external logs")
        data = {'logs':'NO MATCH CHITCHAT **** '+ request_json['query']}
        resp = requests.post(LOGGING_URL,data=data)
        assert resp.status_code == 201

    logging.info(response)
    return jsonify(response)

def get_cached_vector(index_key):
    vector_key = index_key + "_vector"
    return app.config['cache'].get(vector_key)

def get_cached_data(index_key):
    vector_key = index_key +  "_data"
    return app.config['cache'].get(vector_key)

def set_cached_vector(index_key, data):
    vector_key = index_key +  "_vector"
    return app.config['cache'].set(vector_key,data)

def set_cached_data(index_key, data):
    data_key = index_key +  "_data"
    return app.config['cache'].set(data_key, data)

def set_all_projects(project_id, version_id):
    project_key = str(project_id)+ "_" + str(version_id)
    set_all_indexes = app.config['cache'].get('all_indexes')
    set_all_indexes.extend(project_key)
    return app.config['cache'].set('all_indexes', set_all_indexes)

def create_new_index(data_list, question_list):
    index_key = "qa_index"
    # create index
    vector = app.config['model'].encode(question_list)
    index_key = "qa_index"
    app.config['vector'][index_key]=vector
    app.config['data'][index_key]=data_list

    # push to cache
    assert set_cached_vector(index_key, vector)
    assert set_cached_data(index_key, data_list)

@app.route('/create-index', methods=['GET'])
def create_index():
    '''
    # Question list is of the form 
    [ 
        {'question':'This is a question', 'answer': 'This is a ans'}, 
        {'question':'This is a question', 'answer': 'This is a ans'} 
    ]
    '''
    logging.info("calculating vector index for query")
    request_json = json.loads(request.data, strict=False)

    must = ['question_list']

    for key in must:
        if key not in request_json.keys():
            return jsonify({"message": "request does not contain "+key})

    question_list = [obj['answer'] for obj in request_json['question_list']]
    data = request_json['question_list']

    create_new_index(data_list=data, question_list=question_list)
    return jsonify({"message": "index created"})


@app.route('/get-vector', methods=['GET'])
def get_vector():
    """
    Retrieve the embedding of the query
    """
    logging.info("calculating vector for query")
    request_json = json.loads(request.data, strict=False)
    
    if 'query' not in request_json.keys():
        return jsonify({"message": "request does not contain query"})

    vector = app.config['model'].encode(
            preprocess(request_json['query'])
        )

    response = {
        'query' : request_json['query'],
        'vector' : vector.tolist()
    }
    logging.info(response)
    return jsonify(response)

@app.route('/reset')
def reset():
    """
    App index to check whether it is up and running.
    """
    app.config['cache'].clear()
    return 'cache has been cleared'

@app.route('/')
def hello_world():
    """
    App index to check whether it is up and running.
    """
    return 'Hello, World! The service is up for serving vectors to the world :-)\n'

@app.route('/health')
def health_check():
    """
    Health check used for liveness and readiness probes.
    """
    return 'OK\n', 200

@app.route('/pull-data')
def pull_data():
    """
    Health check used for liveness and readiness probes.
    """

    version = request.args.get("version")
    _type = request.args.get("type")

    logging.info("update api called with version "+str(version) + "and type" + _type)

    params = {
        "version":version,
        "type":_type
    }

    version_api = requests.get(VERSION_URL, params=params).json()
    results = version_api["results"]

    while version_api["next"]:
        version_api = requests.get(version_api["next"]).json()
        results.extend(version_api["results"])

    data_list = [{"question": obj['question'], "answer": obj['answer']} for obj in results]
    question_list = [preprocess(obj['question']) for obj in data_list]
    
    create_new_index(data_list=data_list, question_list=question_list)
    return jsonify({"message": "index created"})