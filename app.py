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
    return flask.jsonify(answer)

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
    return flask.jsonify(answer)

app.run(port=8000)