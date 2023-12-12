import flask
import os
from utils.crawler import crawl
from urllib.parse import urlparse
from utils.context import answer_question
import pandas as pd
import openai
openai.api_key = os.environ['OPENAI_API_KEY']

app = flask.Flask(__name__)
app.config["DEBUG"] = True

@app.route('/web_qa', methods=['GET'])
def home():
    try:
        url = flask.request.args.get('url')
        question = flask.request.args.get('question')
    except:
        return flask.jsonify("Error: URL and question parameters are required.")
    domain =  urlparse(url).netloc
    print(domain)
    if not os.path.exists(f'processed/{domain}_embed.pkl'):
        crawl(url)
        
    df = pd.read_pickle(f'processed/{domain}_embed.pkl')
    answer = answer_question(df, question)
    
    return flask.jsonify(answer)

app.run()