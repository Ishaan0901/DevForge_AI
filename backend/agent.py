from langgraph.graph import StateGraph,START,END, add_messages
from langgraph.prebuilt import ToolNode,tools_condition
from langchain.messages import SystemMessage
from typing import TypedDict,Annotated,List
from dotenv import load_dotenv
from model import llm,tools
load_dotenv()



#                                                           State:
class ChatState(TypedDict):
    messages: Annotated[List,add_messages]



#                                                            Nodes:

def llm_node(state:ChatState):
    messages=state['messages']

    prompt=SystemMessage(content='''
    You are DevForge AI, a coding agent.

    First decide: is this a website request or a Python request?

    WEBSITE requests (website, web page, frontend):
    1. Write ONE complete index.html (CSS in <style>, JS in <script>).
    2. Call write_html_code with the code.
    3. Do NOT call write_code, execute_code, or check_result.
    4. Do not use external files or images. Use CSS colors and emojis.
    5. Make it responsive and clean.
    6. After saving, reply with one short line: the website is ready.

    PYTHON requests (everything else):
    1. Write complete Python code.
    2. Call write_code with the code.
    3. Call execute_code with file_name='generated_code.py'.
    4. Call check_result with the dict returned by execute_code.
    5. If it failed, read the error, fix the code, and repeat from step 2.
    6. Try at most 3 fixes. After that, stop and show the error.
    7. When it succeeds, show the final code and output.
    8. Never use input() in the code.

    RULES:
    - Send only raw code to the tools, no explanations inside.
    - Do not skip any step.   
''')


    response=llm.invoke([prompt]+ messages)
    return {'messages':response}


tool_node=ToolNode(tools)



#                                                           Graph:

builder=StateGraph(ChatState)


builder.add_node('llm_node',llm_node)
builder.add_node('tools',tool_node)


builder.add_edge(START,'llm_node')
builder.add_conditional_edges('llm_node',tools_condition,{
    END:END,
    'tools':'tools'
})
builder.add_edge('tools','llm_node')

graph=builder.compile()