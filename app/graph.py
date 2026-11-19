
import re
from typing import TypedDict

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.types import interrupt

from app.tools import cover_balance_tracker
from app.vectorstore import semantic_search

# -----------------------------
# Agent State
# -----------------------------

class AgentState(TypedDict, total=False):
    message: str
    tool_used: str
    result: dict
    citations: list
    planned_package: int
    requires_approval: bool
    approval_status: str
    answer: str
    conversation_history: list


# -----------------------------
# 1. Route User Request
# -----------------------------

def route_request(state: AgentState):

    message = state["message"].lower()

    cover_keywords = [
        "balance",
        "remaining cover",
        "coverage used",
        "family cover",
        "claim",
        "hospital package",
        "package cost",
        "cover left"
    ]

    if any(word in message for word in cover_keywords):
        return "cover_balance"

    return "rag_search"


# -----------------------------
# 2. Cover Balance Tool
# -----------------------------

def cover_balance_node(state: AgentState):

    message = state["message"]

    numbers = re.findall(r"\d[\d,]*", message)

    planned_package = 0

    if numbers:
        planned_package = int(numbers[-1].replace(",", ""))

    result = cover_balance_tracker(
        planned_package=planned_package
    )

    requires_approval = (
        planned_package > result["remaining_amount"]
    )

    return {
        "tool_used": "cover_balance_tracker",
        "result": result,
        "planned_package": planned_package,
        "requires_approval": requires_approval
    }


# -----------------------------
# 3. RAG Search Tool
# -----------------------------

def rag_search_node(state: AgentState):

    message = state["message"]
    history = state.get("conversation_history", [])

    # Check whether the user previously shared their name
    if "name" in message.lower():

        for item in reversed(history):

            if item["role"] == "user":

                match = re.search(
                    r"\bmy name is\s+([A-Za-z][A-Za-z ]*)",
                    item["content"],
                    re.IGNORECASE
                )

                if match:
                    name = match.group(1).strip()

                    return {
                        "tool_used": "conversation_memory",
                        "answer": f"Your name is {name}."
                    }

    results = semantic_search(
        query=message,
        n_results=5
    )

    citations = []

    for item in results:

        metadata = item.get("metadata", {})

        citations.append({
            "chunk_id": item.get("chunk_id"),
            "document": metadata.get("title"),
            "page": metadata.get("page"),
            "source": metadata.get("source")
        })

    return {
        "tool_used": "rag_search",
        "result": {"results": results},
        "citations": citations,
        "answer": (
            "Relevant healthcare information was retrieved."
            if results
            else "I don't know. No relevant information was found."
        )
    }


# -----------------------------
# 4. Human Approval Node
# -----------------------------

def approval_node(state: AgentState):

    result = state["result"]

    decision = interrupt({
        "message": (
            "The planned hospital package exceeds the "
            "remaining family coverage. Do you approve proceeding?"
        ),
        "planned_package": state["planned_package"],
        "remaining_amount": result["remaining_amount"],
        "excess_amount": (
            state["planned_package"] - result["remaining_amount"]
        )
    })

    if isinstance(decision, dict):
        approved = decision.get("approved", False)
    else:
        approved = decision is True

    if approved:
        return {
            "approval_status": "approved",
            "answer": (
                "Approval received. The package still exceeds "
                "the remaining coverage. Please confirm the "
                "arrangement with the relevant authority."
            )
        }

    return {
        "approval_status": "rejected",
        "answer": "The planned package was not approved."
    }


# -----------------------------
# 5. Decide Whether Approval Is Needed
# -----------------------------

def check_approval(state: AgentState):

    if state.get("requires_approval"):
        return "approval"

    return "save_history"


# -----------------------------
# 6. Save Conversation History
# -----------------------------

def save_history(state: AgentState):

    history = state.get("conversation_history", [])

    history = history + [
        {
            "role": "user",
            "content": state["message"]
        },
        {
            "role": "assistant",
            "content": state.get("answer", "")
        }
    ]

    return {
        "conversation_history": history
    }


# -----------------------------
# 7. Build LangGraph
# -----------------------------

builder = StateGraph(AgentState)

builder.add_node("cover_balance", cover_balance_node)
builder.add_node("rag_search", rag_search_node)
builder.add_node("approval", approval_node)
builder.add_node("save_history", save_history)

builder.add_conditional_edges(
    START,
    route_request,
    {
        "cover_balance": "cover_balance",
        "rag_search": "rag_search"
    }
)

builder.add_conditional_edges(
    "cover_balance",
    check_approval,
    {
        "approval": "approval",
        "save_history": "save_history"
    }
)

builder.add_edge("approval", "save_history")
builder.add_edge("rag_search", "save_history")
builder.add_edge("save_history", END)


# Memory: retain conversation state by thread ID

memory = InMemorySaver()

agent_graph = builder.compile(
    checkpointer=memory
)

