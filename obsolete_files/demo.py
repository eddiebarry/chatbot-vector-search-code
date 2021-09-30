"""
Knowledge base preparation.
"""


import json 
# import fasttext
# import faiss
import pickle
import logging
import sys

from sentence_transformers import SentenceTransformer, util
from preprocessing import preprocess

model = SentenceTransformer('/app/vector/paraphrase-MiniLM-L6-v2')

logging.basicConfig(
    stream=sys.stdout,
    level=logging.DEBUG,format='%(asctime)s %(levelname)-8s %(funcName)s %(message)s',
    datefmt="%Y-%m-%dT%H:%M:%S%z")

def populate_questions(project_id, version_id):
    f = open("./production_data/chitchat_answers.json",)
    chitchat_data = json.load(f)
    f.close()

    question_list = []
    for question in chitchat_data.keys():
        new_obj = {
            # applying the same preprocessing that is applied to user queries:
            "question": preprocess(question),
            "answer": chitchat_data[question]
        }
        question_list.append(new_obj)

    req = {
        "project_id": project_id,
        "version_id": version_id,
        "question_list": question_list
    }

    return req




def set_up_knowledge_base(request_json):
    request_json = populate_questions(
        project_id=0,
        version_id=0
    )

    data_list = request_json['question_list']
    question_list = [obj['question'] for obj in data_list]
    project_id = request_json['project_id']
    version_id = request_json['version_id']

    vector = model.encode(question_list)
    index_key = str(project_id) + "_" + str(version_id)

    big_obj = {
        "key": index_key,
        "vector": vector,
        "project_id": project_id,
        "version_id": version_id,
        "data_list": data_list
    }

    with open('./vectors.pickle', 'wb') as handle:
        pickle.dump(big_obj, handle, protocol=pickle.HIGHEST_PROTOCOL)



#     """
#     Process and index the knowledge base and create the required mappings for
#     searching questions and retrieving replies.
#     """
#     if not ft:
#         ft = fasttext.load_model(model_dir)


#     ft.get_sentence_vector("My name is jeff")[:10]
#     logging.debug(ft.get_sentence_vector("My name is jeff")[:10])


    

#     f = open("./production_data/labelled_data.json",)
#     data = json.load(f)

#     vec_labels = {}
#     for x in data.keys():
#         vec_labels[x] = (x,ft.get_sentence_vector(preprocess(x)))


#     a = np.empty([0,300])
#     for x in vec_labels.keys():
#         vec = vec_labels[x][1]
#         a = np.concatenate((a,np.expand_dims(vec,axis=0)),axis=0)


    

#     index = faiss.IndexIDMap2(faiss.IndexFlatL2(300))

#     # add vectors to the index
#     index.add_with_ids(np.float32(a),np.arange(a.shape[0]))                  

#     faiss.write_index(index, "/storage/chitchat_faq.bin")
#     f = open("./production_data/chitchat_answers.json",)
#     chitchat_data = json.load(f)
#     f.close()

#     id_chitchat_answer = {}
#     id_chitchat_question = {}
#     id_chitchat_vector = {}


#     chitchat_vecs = np.empty([0,300])
#     chitchat_ids = np.empty([0])

#     chitchat_id = 0
#     for x in data.keys():
#         if data[x]==1:
#             id_chitchat_answer[chitchat_id] = chitchat_data[x]
#             id_chitchat_question[chitchat_id] = x
#             id_chitchat_vector[chitchat_id] = np.float32(ft.get_sentence_vector(x))

#             chitchat_vecs = np.concatenate(
#                 (chitchat_vecs,np.expand_dims(id_chitchat_vector[chitchat_id], axis=0))
#             )
#             chitchat_ids = np.concatenate(
#                 (chitchat_ids, np.array([chitchat_id],dtype=np.int))
#             )
#             chitchat_id += 1


#     # json_file_name = "id_chitchat_answer.json"
#     json_file_name = "/storage/id_chitchat_answer.json"
#     print("writing", json_file_name)
#     with open(json_file_name , 'w') as json_file:
#         json.dump(id_chitchat_answer, json_file,        indent = 4, sort_keys=True)

#     # json_file_name = "id_chitchat_question.json"
#     json_file_name = "/storage/id_chitchat_question.json"
#     print("writing", json_file_name)
#     with open(json_file_name , 'w') as json_file:
#         json.dump(id_chitchat_question, json_file,        indent = 4, sort_keys=True)

#     chitchat_vecs = np.float32(chitchat_vecs)
#     chitchat_ids = chitchat_ids.astype(int)

if __name__ == '__main__':
    set_up_knowledge_base()
