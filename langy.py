from langchain.tools import tool

@tool
def get_weather(city: str) -> str:
    """Returns the current weather in a given city."""
    return f"The weather in {city} is sunny ☀️."

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import AIMessage, HumanMessage, ToolMessage, SystemMessage
from langchain_core.tools import ToolCall
from typing import List, Optional, Any

class ChatLLaMA3(BaseChatModel):
    model: AutoModelForCausalLM
    tokenizer: AutoTokenizer
    temperature: float = 0.7
    max_new_tokens: int = 512

    def _convert_messages_to_prompt(self, messages: List[Any]) -> str:
        return self.tokenizer.apply_chat_template(messages, return_tensors=None, add_generation_prompt=True)

    def _generate(self, messages: List[Any], stop: Optional[List[str]] = None) -> AIMessage:
        prompt = self._convert_messages_to_prompt(messages)
        input_ids = self.tokenizer(prompt, return_tensors="pt").to(self.model.device)
        outputs = self.model.generate(
            **input_ids,
            max_new_tokens=self.max_new_tokens,
            temperature=self.temperature,
            do_sample=True
        )
        decoded = self.tokenizer.decode(outputs[0], skip_special_tokens=True)

        content = decoded.split("<|assistant|>")[-1].strip()

        # Optionally: parse for tool_call here if needed
        return AIMessage(content=content)

llm = ChatLLaMA3(model=model, tokenizer=tokenizer)
llm_with_tools = llm.bind_tools([get_weather])

from langchain_core.runnables import Runnable
from langgraph.graph import StateGraph, END

class AgentState(dict): pass

def call_agent(state: AgentState):
    user_input = state["input"]
    response = llm_with_tools.invoke([HumanMessage(content=user_input)])
    return {"input": user_input, "response": response}

def tool_router(state: AgentState):
    response = state["response"]
    tool_calls = response.tool_calls if hasattr(response, "tool_calls") else []
    outputs = []

    for call in tool_calls:
        if call["name"] == "get_weather":
            result = get_weather.invoke(call["args"])
            outputs.append(ToolMessage(tool_call_id=call["id"], content=result))

    return {"input": state["input"], "tool_messages": outputs}

builder = StateGraph(AgentState)
builder.add_node("agent", call_agent)
builder.add_node("tool_caller", tool_router)

builder.add_edge("agent", "tool_caller")
builder.add_edge("tool_caller", "agent")  # loop back if needed
builder.set_entry_point("agent")
builder.set_finish_point("agent")  # or add a condition to stop

graph = builder.compile()

response = graph.invoke({"input": "What's the weather in Bangalore?"})
print(response["response"].content)
