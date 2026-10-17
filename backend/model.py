from langchain_groq import ChatGroq
from dotenv import load_dotenv
from tools import write_code,check_result,execute_code,write_html_code
load_dotenv()


model=ChatGroq(
    model='openai/gpt-oss-20b',
    temperature=0
)

tools=[write_code,check_result,execute_code,write_html_code]

llm=model.bind_tools(tools)