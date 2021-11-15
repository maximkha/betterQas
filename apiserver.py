from flask import Flask
from flask import request
from quizAdapter import *

app = Flask(__name__)

STR_TO_TYPE = {"mc": AnswerType.MULTICHOICE, "tf": AnswerType.TF}

@app.after_request
def after_request_func(response):
    origin = request.headers.get('Origin')
    if request.method == 'OPTIONS':
        response = make_response()
        response.headers.add('Access-Control-Allow-Credentials', 'true')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        response.headers.add('Access-Control-Allow-Headers', 'x-csrf-token')
        response.headers.add('Access-Control-Allow-Methods',
                            'GET, POST, OPTIONS, PUT, PATCH, DELETE')
        if origin:
            response.headers.add('Access-Control-Allow-Origin', origin)
    else:
        response.headers.add('Access-Control-Allow-Credentials', 'true')
        if origin:
            response.headers.add('Access-Control-Allow-Origin', origin)

    return response

@app.route('/')
def hello():
    question = request.args.get('question')
    qtype = request.args.get('qtype')
    if question == None or qtype == None:
        return {"error":True, "message": "query params", "results":[], "question":question, "qtype": qtype}

    if qtype not in STR_TO_TYPE:
        return {"error":True, "message": "qtype", "results":[], "question":question, "qtype": qtype}

    results = query(question, STR_TO_TYPE[qtype])
    print(results)
    return {"error":False, "message": "ok", "results":results, "question":question, "qtype": qtype}

if __name__ == '__main__':
    app.run()