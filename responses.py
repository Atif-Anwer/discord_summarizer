import os
import time
from random import randint
from typing import Final

from dotenv import load_dotenv
from openai import OpenAI


def load_openai_client_asistant():
    client       = OpenAI( api_key = os.getenv("OPENAI_API_KEY") )
    assistant_id = client.beta.assistants.retrieve( str( os.getenv("ASSISTANT_ID")))
    thread       = client.beta.threads.create()

    return client, assistant_id, thread

# check in loop  if assistant ai parse our request
def wait_on_run(run, thread):
    while run.status == "queued" or run.status == "in_progress":
        run = client.beta.threads.runs.retrieve(
            thread_id = thread.id,
            run_id    = run.id,
        )
        time.sleep(0.5)
    return run

def get_response_from_gpt(user_prompt: str) -> str:

    user_prompt: str = user_prompt.lower()

    # Hardcoded text replies for testing
    if user_prompt == ' ':
        return 'Well, you\'re awfully silent...'
    elif 'hello' in user_prompt:
        return 'Hello there!'
    elif 'how are you' in user_prompt:
        return 'Good, thanks!'
    elif 'bye' in user_prompt:
        return 'See you!'
    elif 'roll dice' in user_prompt:
        return f'You rolled: {randint(1, 6)}'

    # -------------------------------

    # Add a message to the thread
    message = client.beta.threads.messages.create(
        thread_id = assistant_thread.id,
        role      = "user",
        content   = user_prompt,
    )

    # Run the assistant
    run = client.beta.threads.runs.create(
        thread_id    = assistant_thread.id,
        assistant_id = assistant_id.id,
    )

    # Retreive the assistant run on the prompt
    run = wait_on_run(run, assistant_thread)

    # Print out all the messages added after our last user message
    messages = client.beta.threads.messages.list(
        thread_id = assistant_thread.id,
        order     = "asc",
        after     = message.id
    )

    print (message.role + ":" + message.content[0].text.value)

    return messages.data[0].content[0].text.value


load_dotenv()
OPENAI_TOKEN: Final[str]                = os.getenv("OPENAI_API_KEY")
client, assistant_id, assistant_thread  = load_openai_client_asistant()
# print(assistant_id)

# References:
# https://youtu.be/5rcjGjgJNQc