# Web  Q&A with Embeddings

Learn how to crawl your website and build a Q/A bot with the OpenAI API. You can find the full tutorial in the [OpenAI documentation](https://platform.openai.com/docs/tutorials/web-qa-embeddings).

## To run the server:

```
python -m venv venv
pip install -r requirements.txt
python app.py
```

## Flowchart of Design

```mermaid
graph TD;

a(web_qa request)
b{already crawled}
c(ask ChatGPT)
d(crawl and save embedding)
e(return Answer)
a -->b
b --yes--> c
b --no--> d
d --> c
c --> e

```
