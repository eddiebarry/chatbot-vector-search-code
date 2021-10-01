# import requests
# import json


# base_url = "http://feature-word-embeddings-vla-chitchat-labs-dev.apps.dev.lxp.academy.who.int"
# base_url = "http://vla-chitchat-labs-staging.apps.dev.lxp.academy.who.int"
# base_url = "http://feature-autmation-vla-search-labs-dev.apps.dev.lxp.academy.who.int"
# base_url = "http://feature-autmation-vla-chitchat-labs-dev.apps.dev.lxp.academy.who.int"

base_url = "0.0.0.0:8000"
# base_url ="http://feature-new-data-test-vla-search-labs-dev.apps.dev.lxp.academy.who.int"

# # qry = 'do you like tacos and burritos and quentin tarantino ?'

# # params = {
# #     "query": qry,
# # }

# # r = requests.get(base_url+"/get-vector", data=json.dumps(params))
# # response  = r.json()
# # import pdb; pdb.set_trace()

# # # Create Index once
# # params = {
# #     "question_list": [ 
# #         {'question':'When will the academy be available', 'answer': 'This is a ans for academy avail'}, 
# #         {'question':'How can i change my profile picture', 'answer': 'This is a ans for profile picture'} 
# #     ],
# #     "project_id":"1",
# #     "version_id":"1",
# # }

# # r = requests.get(base_url+"/create-index", data=json.dumps(params))
# # response  = r.json()
# # import pdb; pdb.set_trace()


# # # Create index again
# # params = {
# #     "question_list": [ 
# #         {'question':'When will the academy be available', 'answer': 'This is a ans for academy avail'}, 
# #         {'question':'How can i change my profile picture', 'answer': 'This is a ans for profile picture'} 
# #     ],
# #     "project_id":"1",
# #     "version_id":"1",
# # }

# # r = requests.get(base_url+"/create-index", data=json.dumps(params))
# # response  = r.json()

# # import pdb; pdb.set_trace()



# get closest
for x in range(10):
    import requests, json
    params = {
        "query": "when will it be available",
    }

    r = requests.get(base_url+"/get-closest", data=json.dumps(params))
    response  = r.json()
    print(response)
import pdb; pdb.set_trace()

# # # get closest top_k
# # params = {
# #     "query": "when will it be available",
# #     "project_id":"1",
# #     "version_id":"1",
# #     "top_k": "1"
# # }

# # r = requests.get(base_url+"/get-closest", data=json.dumps(params))
# # response  = r.json()
# # import pdb; pdb.set_trace()


# params = {
#     "query": "hey baby could you show me a good time. i like to read",
# }

# r = requests.get(base_url+"/get-chitchat", data=json.dumps(params))
# response  = r.json()
# import pdb; pdb.set_trace()

# params = {
#     "query": "where can i find the campus in lyon after   i change my profile picture for learning content",
# }

# r = requests.get(base_url+"/get-closest", data=json.dumps(params))
# response  = r.json()
# import pdb; pdb.set_trace()