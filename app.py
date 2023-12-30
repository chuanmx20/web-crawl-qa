import flask
import os
from utils.crawler import crawl
from urllib.parse import urlparse
from utils.context import answer_question
import pandas as pd
import openai
import prompts
openai.api_key = os.environ['OPENAI_API_KEY']

app = flask.Flask(__name__)
app.config["DEBUG"] = True

def json_response(data):
    # include Access-Control-Allow-Origin: *
    response = flask.jsonify(data)
    response.headers.add("Access-Control-Allow-Origin", "*")
    return flask.jsonify(data)

@app.route('/web_qa', methods=['GET'])
def web_qa():
    try:
        url = flask.request.args.get('url')
        question = flask.request.args.get('question')
    except Exception as e:
        return flask.jsonify(f"Error: URL and question parameters are required. ERROR: {e}")
    # domain =  urlparse(url).netloc
    # print(domain)
    # if not os.path.exists(f'processed/{domain}_embed.pkl'):
    #     crawl(url)
    # df = pd.read_pickle(f'processed/{domain}_embed.pkl')
    answer = answer_question(model="gpt-4", prompt=prompts.qa_template.format(question=question, url=url), instruction=prompts.qa_guide)
    answer = prompts.extract_answer(answer)
    return json_response(answer)

@app.route('/suggestion', methods=['GET'])
def suggestion():
    try:
        url = flask.request.args.get('url')
    except Exception as e:
        return flask.jsonify(f"Error: URL and question parameters are required. ERROR: {e}")
    # domain =  urlparse(url).netloc
    # print(domain)
    # if not os.path.exists(f'processed/{domain}_embed.pkl'):
    #     crawl(url)
    # df = pd.read_pickle(f'processed/{domain}_embed.pkl')
    answer = answer_question(model="gpt-4", prompt=prompts.suggestion_template.format(url=url), instruction=prompts.suggestion_guide)
    answer = prompts.extract_answer(answer)
    return json_response(answer)

app.run(port=8000)