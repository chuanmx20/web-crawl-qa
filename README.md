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

a(web_qa Request)
b{Site Already Crawled}
c(Ask ChatGPT)
d(Crawl and Save Embedding)
e(Return Answer)
a -->b
b --yes--> c
b --no--> d
d --> c
c --> e

```

## API Reference

| PATH        | PARAMS                                                                                                             | HEADER | BODY | NOTE |
| ----------- | ------------------------------------------------------------------------------------------------------------------ | ------ | ---- | ---- |
| /web_qa     | question(str): question to ask about the site<br />url(str): url of the site to ask, https://baidu.com for example | --     | --   | --   |
| /suggestion |                                                                                                                    |        |      |      |
