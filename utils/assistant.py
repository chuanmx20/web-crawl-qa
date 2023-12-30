import openai
from openai import OpenAI
import tempfile
from prompts import assistant_instructions as instructions
client = OpenAI()

def create_retrieval_assistant(instructions:str, file_id: str):
    """create a retrieval assistant

    Args:
        instructions (str): instructions for the assistant
        file_id (str): file id

    Returns:
        str: assistant id
    """
    response = client.beta.assistants.create(
        instructions=instructions,
        model="gpt-4-1106-preview",
        tools=[{"type": "retrieval"}],
        file_ids=[file_id]
    )
    return response['id']

def upload_file(html: str):
    """upload html to openai

    Args:
        html (str): html string of one page

    Returns:
        str: file id
    """
    # create a temp file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.html') as f:
        f.write(html)
        f.seek(0)
        # upload the file
        response = client.files.create(file=open(f.name, 'rb'), purpose='search')
        return response['id']

def create_therad_and_run(prompt, assistant_id, file_id):
    """create a thread and run it

    Args:
        assistant_id (str): assistant id
        prompt (str): prompt
    """
    thread = client.beta.threads.create()
    client.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content=prompt,
        file_ids=[file_id]
    )
    run = client.beta.threads.runs.create(
        thread_id=thread.id,
        assistant_id=assistant_id
    )
    
    while True:
        retrieve_run = client.beta.threads.runs.retrieve(
            thread_id=thread.id,
            run_id=run.id
        )
        if retrieve_run.status == "completed":
            break
        
    messages = client.beta.threads.messages.list(
        thread_id=thread.id
    )
    for message in messages:
        try:
            return message.content[0].text.value
        except Exception as e:
            return str(e)