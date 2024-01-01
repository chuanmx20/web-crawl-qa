import flask
import os
from utils.crawler import crawl
from urllib.parse import urlparse
from utils.context import answer_question
from utils import assistant
import pandas as pd
import openai
import prompts
import sqlite3
import time
openai.api_key = os.environ['OPENAI_API_KEY']

app = flask.Flask(__name__)
app.config["DEBUG"] = True

# read the database
# check if db exists
if not os.path.exists('db.sqlite3'):
    # create db
    conn = sqlite3.connect('db.sqlite3')
    # create table
    conn.execute('''CREATE TABLE uploaded_html
            (ID INTEGER PRIMARY KEY AUTOINCREMENT,
            url TEXT NOT NULL,
            file_id TEXT NOT NULL,
            assistant_id TEXT
            );''')
    conn.close()
    

def json_response(data, origin="*"):
    # include Access-Control-Allow-Origin: *
    response = flask.jsonify(data)
    response.headers.add("Access-Control-Allow-Origin", origin)
    response.headers.add("Access-Control-Allow-Credentials", "true")
    return response

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

def get_ids_from_db(url):
    conn = sqlite3.connect('db.sqlite3')
    search = conn.execute(f"SELECT assistant_id, file_id FROM uploaded_html WHERE url = '{url}'").fetchone()
    conn.close()
    if not search:
        return False
    assistant_id = search[0]
    file_id = search[1]
    
    return assistant_id, file_id

@app.route('/upload', methods=['POST'])
def upload():
    try:
        url = flask.request.args.get('url')
        html = flask.request.form['html']
    except Exception as e:
        return flask.jsonify(f"Error: HTML and URL parameters are required. ERROR: {e}", 400)
    
    conn = sqlite3.connect('db.sqlite3')
    if conn.execute(f"SELECT * FROM uploaded_html WHERE url = '{url}'").fetchone():
        return json_response({"status": "success"})
    # upload html to openai
    file_id = assistant.upload_file(html)
    assistant_id = assistant.create_retrieval_assistant(instructions=prompts.assistant_instructions, file_id=file_id)
    # save to database
    conn.execute(f"INSERT INTO uploaded_html (url, file_id, assistant_id) VALUES ('{url}', '{file_id}', '{assistant_id}')")
    conn.commit()
    conn.close()
    return json_response({"status": "success"})


@app.route('/assistant_qa', methods=['GET'])
def assistant_qa():
    try:
        url = flask.request.args.get('url')
        question = flask.request.args.get('question')
    except Exception as e:
        return json_response(f"Error: URL and question parameters are required. ERROR: {e}")

    prompt = prompts.assistant_qa_template.format(question=question, url=url, guide=prompts.assistant_qa_guide)
    
    flag = False
    while not flag:
        # get assistant id and file id
        ids = get_ids_from_db(url)
        if not ids:
            time.sleep(1)
            continue
        assistant_id, file_id = ids
        
        # inference
        answer = assistant.create_therad_and_run(prompt=prompt, assistant_id=assistant_id, file_id=file_id)
        answer = prompts.extract_answer(answer)
        if answer:
            flag = True
            break

    return json_response(answer)

@app.route('/assistant_suggestion', methods=['GET'])
def assistant_suggestion():
    try:
        url = flask.request.args.get('url')
    except Exception as e:
        return json_response(f"Error: URL and question parameters are required. ERROR: {e}")
    
    prompt = prompts.assistant_suggestion_template.format(url=url)
    flag = False
    while not flag:
        # get assistant id and file id
        ids = get_ids_from_db(url)
        if not ids:
            time.sleep(1)
            continue
        assistant_id, file_id = ids
        
        # inference
        answer = assistant.create_therad_and_run(prompt=prompt, assistant_id=assistant_id, file_id=file_id)
        answer = prompts.extract_answer(answer)
        if answer:
            flag = True
            break
    return json_response(answer)

app.run(port=8000)