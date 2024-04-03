import requests
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage
from dotenv import load_dotenv
import os
from requests.exceptions import HTTPError, Timeout

load_dotenv()

OPEN_AI_KEY = os.getenv("OPENAI_API_KEY")
AI_DEVS_KEY = os.getenv("AIDEVS_API_KEY")
TOKEN = "https://tasks.aidevs.pl/token/scraper"
ANSWER = "https://tasks.aidevs.pl/answer"
TASK = "https://tasks.aidevs.pl/task"
TOKEN_PARAMS = {
    "apikey": AI_DEVS_KEY
}

token_response = requests.post(url=TOKEN, json=TOKEN_PARAMS)
token_response.raise_for_status()
token_data = token_response.json()
token = token_data["token"]

get_task_response = requests.get(url=f"{TASK}/{token}")
token_response.raise_for_status()
task_data = get_task_response.json()

scrap_url = task_data["input"]
question = task_data["question"]
system_msg = task_data["msg"]

headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/58.0.3029.110 Safari/537.3'
    }

try:
    page = requests.get(url=scrap_url, headers=headers, timeout=120)
    page_text = page.text

    chat = ChatOpenAI(api_key=OPEN_AI_KEY)
    system_prompt = f"{system_msg}./n {page_text}"
    system_message = {"role": "system", "content": system_prompt}
    human_message = HumanMessage(content=question)
    response = chat.invoke([system_message, human_message])
    answer = {
        "answer": response.content
    }
    send_answer = requests.post(url=f"{ANSWER}/{token}", json=answer)

except HTTPError as http_err:
    print(f'HTTP error occurred: {http_err} - Status Code: {http_err.response.status_code}')
    if http_err.response.status_code == 500:
        print("Server Error - The server encountered an unexpected condition.")

except Timeout:
    print('The request timed out; try again later.')

