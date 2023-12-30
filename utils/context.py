from openai import OpenAI

client = OpenAI() 
from utils.embeddings_utils import distances_from_embeddings
def create_context(question, df, max_len=1800):
    """
    Create a context for a question by finding the most similar context from the dataframe
    """

    # Get the embeddings for the question
    q_embeddings = client.embeddings.create(input=question, model='text-embedding-ada-002').data[0].embedding
    # Get the distances from the embeddings
    df['distances'] = distances_from_embeddings(q_embeddings, df['embeddings'], distance_metric='cosine')


    returns = []
    cur_len = 0

    # Sort by distance and add the text to the context until the context is too long
    for i, row in df.sort_values('distances', ascending=True).iterrows():
        
        # Add the length of the text to the current length
        cur_len += row['n_tokens'] + 4
        
        # If the context is too long, break
        if cur_len > max_len:
            break
        
        # Else add it to the text that is being returned
        returns.append(row["text"])

    # Return the context
    return "\n\n###\n\n".join(returns)

def answer_question(
    # df,
    model="gpt-4",
    prompt="",
    instruction="",
    max_len=1800,
    debug=False,
    max_tokens=512,
    stop_sequence=None
):
    """
    Answer a question based on the most similar context from the dataframe texts
    """
    # context = create_context(
    #     prompt,
    #     df,
    #     max_len=max_len,
    # )

    try:
        messages = [
            {"role":"system","content":instruction},
            {"role":"user","content": prompt}
        ]
        # print(messages)
        # Create a completions using the question and context
        response = client.chat.completions.create(
            messages=messages,
            model = model,
            max_tokens = max_tokens,
            stream=False
        )
        return response.choices[0].message.content
    except Exception as e:
        print(e)
        return f"error: {e}"
    