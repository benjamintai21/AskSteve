import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import google.generativeai as genai
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
from langchain.schema import SystemMessage, HumanMessage
from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferMemory

import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from langchain.tools import Tool, DuckDuckGoSearchResults
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.agents import initialize_agent, AgentType
from langchain.agents import AgentType
from langchain.memory import ConversationBufferMemory
from langchain.agents import load_tools

from langchain_community.utilities import GoogleSerperAPIWrapper

# ddg_search = DuckDuckGoSearchResults()
search = GoogleSerperAPIWrapper()
# duckduckgo_tool = Tool(
#     name="DuckDuckGoSearch",
#     func=ddg_search.run,   # runs the search query
#     description="Use this to search the internet for up-to-date information."
# )

serper = Tool(
    name="DuckDuckGoSearch",
    func=search.run,   # runs the search query
    description="Use this to search the internet for up-to-date information."
)


def parse_html(content) -> str:
    soup = BeautifulSoup(content, 'html.parser')
    text_content_with_links = soup.get_text()
    return text_content_with_links

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:90.0) Gecko/20100101 Firefox/90.0'
}

def fetch_web_page(url: str) -> str:
    response = requests.get(url, headers=HEADERS)
    return parse_html(response.content)

web_fetch_tool = Tool.from_function(
    func=fetch_web_page,
    name="WebFetcher",
    description="Fetches the content of a web page"
)

prompt_template = "Summarize the following content: {content}"
llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash")
llm_chain = LLMChain(
    llm=llm,
    prompt=PromptTemplate.from_template(prompt_template)
)

summarize_tool = Tool.from_function(
    func=llm_chain.run,
    name="Summarizer",
    description="Summarizes a web page"
)

tools = [serper, web_fetch_tool, summarize_tool]

agent = initialize_agent(
    tools=tools,
    agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    llm=llm,
    verbose=True
)

memory = ConversationBufferMemory(memory_key="chat_history")

agent_chain = initialize_agent(tools,
                               llm,
                               agent=AgentType.CONVERSATIONAL_REACT_DESCRIPTION,
                               verbose=True,
                               memory=memory)


app = FastAPI()

# Enable CORS so frontend can access backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Change if your frontend is hosted elsewhere
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    message: str

@app.post("/chat")
async def chat(request: ChatRequest):
    response = agent_chain.run(input=request.message)
    return {"reply": response}

