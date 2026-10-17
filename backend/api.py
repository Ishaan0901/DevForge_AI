import os
import json
import ast
from pydantic import BaseModel
from fastapi import FastAPI
from agent import graph

app = FastAPI()

HTML_PATH = os.path.join("website", "index.html")
PY_PATH = "generated_code.py"


class QueryRequest(BaseModel):
    query: str


def read_file(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def get_last_execution(messages):
    """Find the last execute_code result in the messages."""
    for m in reversed(messages):
        if getattr(m, "name", None) == "execute_code":
            content = m.content
            try:
                return json.loads(content)
            except Exception:
                try:
                    return ast.literal_eval(content)
                except Exception:
                    return {"output": str(content), "error": "", "exit_code": None}
    return None


@app.post("/generate")
def generate(request: QueryRequest):
    # Remove old files so results from older runs don't show up
    for path in (HTML_PATH, PY_PATH):
        if os.path.exists(path):
            os.remove(path)

    try:
        result = graph.invoke(
            {"messages": [request.query]},
            config={"recursion_limit": 15},
        )
        messages = result["messages"]
        final_text = messages[-1].content

        if os.path.exists(HTML_PATH):
            return {
                "type": "website",
                "html": read_file(HTML_PATH),
                "message": final_text,
            }

        code = read_file(PY_PATH) if os.path.exists(PY_PATH) else ""
        execution = get_last_execution(messages) or {}
        return {
            "type": "python",
            "code": code,
            "output": execution.get("output", ""),
            "error": execution.get("error", ""),
            "message": final_text,
        }
    except Exception as e:
        return {"error": str(e)}