import flask
import os
from utils.crawler import crawl
from urllib.parse import urlparse
from utils.context import answer_question
import pandas as pd
import openai

app = flask.Flask(__name__)
app.config["DEBUG"] = True

@app.route('/web_qa', methods=['GET'])
def home():
    url = flask.request.args.get('url')
    question = flask.request.args.get('question')
    domain =  urlparse(url).netloc
    print(domain)
    if not os.path.exists(f'processed/{domain}_embed.csv'):
        crawl(url)
        
    df = pd.read_csv(f'processed/{domain}_embed.csv')
    answer = answer_question(df, question)
    
    return flask.jsonify(answer)

app.run()