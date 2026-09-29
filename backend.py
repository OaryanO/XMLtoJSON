import os
import json
import xmltodict

from dotenv import load_dotenv
from typing import TypedDict

from langchain_groq import ChatGroq
from langchain_core.tools import tool
from langgraph.graph import StateGraph, START, END


load_dotenv()


class State(TypedDict):
    file_path: str
    xml: str
    instruction: str
    result: str
    method: str


@tool
def xml_to_json_tool(xml: str) -> str:
    """Convert XML directly to JSON without restructuring."""
    return json.dumps(
        xmltodict.parse(xml),
        indent=2
    )


llm = ChatGroq(
    model="openai/gpt-oss-120b",
    temperature=0,
    reasoning_effort="medium"
)


def agent(state: State):

    decision_prompt = f"""
You are an XML to JSON agent.

Decide how to handle the user's request.

Use TOOL if the user only wants a normal XML to JSON
conversion while keeping the same structure.

Use LLM if the user wants:
- fields renamed
- fields removed
- fields combined
- nested structures changed
- arrays simplified
- data reorganized
- any semantic transformation

Reply with only one word:
TOOL
or
LLM

User request:
{state["instruction"]}

XML:
{state["xml"]}
"""

    decision = llm.invoke(
        decision_prompt
    ).content.strip().upper()

    if "LLM" in decision:

        prompt = f"""
Convert the following XML into JSON according to
the user's requirement.

User requirement:
{state["instruction"]}

XML:
{state["xml"]}

Return valid JSON only.
Do not include markdown or explanations.
"""

        result = llm.invoke(prompt).content

        return {
            "result": result,
            "method": "LLM"
        }

    result = xml_to_json_tool.invoke({
        "xml": state["xml"]
    })

    return {
        "result": result,
        "method": "XML Parser Tool"
    }


def save_json(state: State):

    try:

        data = json.loads(
            state["result"]
        )

        output_path = os.path.splitext(
            state["file_path"]
        )[0] + ".json"

        with open(
            output_path,
            "w",
            encoding="utf-8"
        ) as f:

            json.dump(
                data,
                f,
                indent=2,
                ensure_ascii=False
            )

        return {
            "result": json.dumps(
                data,
                indent=2,
                ensure_ascii=False
            ),
            "method": state["method"]
        }

    except Exception as e:

        return {
            "result": f"Invalid JSON: {e}",
            "method": state["method"]
        }


graph = StateGraph(State)

graph.add_node(
    "agent",
    agent
)

graph.add_node(
    "save",
    save_json
)

graph.add_edge(
    START,
    "agent"
)

graph.add_edge(
    "agent",
    "save"
)

graph.add_edge(
    "save",
    END
)

app = graph.compile()


def convert_xml(file_path, instruction):

    with open(
        file_path,
        "r",
        encoding="utf-8"
    ) as f:

        xml = f.read()

    result = app.invoke({
        "file_path": file_path,
        "xml": xml,
        "instruction": instruction,
        "result": "",
        "method": ""
    })

    return result