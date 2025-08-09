from dotenv import load_dotenv
from openai import OpenAI
import json
import os
from datetime import datetime
import gradio as gr


load_dotenv(override=True)
google_api_key = os.getenv("GOOGLE_API_KEY")

def log_violation(question_text):
    print(f"Logging violation: {question_text}", flush=True)
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"Datetime: {now} | Question: {question_text}\n"
    with open("violations.txt", "a", encoding="utf-8") as f:
        f.write(line)
    return {"logged": "ok"}


log_violation_json = {
    "name": "log_violation",
    "description": "Use this tool to record any question that violates the guardrails",
    "parameters": {
        "type": "object",
        "properties": {
            "question_text": {
                "type": "string",
                "description": "The question that violated the guardrails"
            }
        },
        "required": ["question_text"],
        "additionalProperties": False
    }
}

tools = [{"type": "function", "function": log_violation_json}]


class ChatGuard:

    def __init__(self):
        self.gemini = OpenAI(base_url="https://generativelanguage.googleapis.com/v1beta/openai/", api_key=google_api_key)
        with open("guardrails.txt", "r", encoding="utf-8") as f:
            self.guardrails = f.read()


    def handle_tool_call(self, tool_calls):
        results = []
        for tool_call in tool_calls:
            tool_name = tool_call.function.name
            arguments = json.loads(tool_call.function.arguments)
            print(f"Tool called: {tool_name}", flush=True)
            tool = globals().get(tool_name)
            result = tool(**arguments) if tool else {}
            results.append({"role": "tool","content": json.dumps(result),"tool_call_id": tool_call.id})
        return results
    
    def system_prompt(self):
        system_prompt = f"You are a chatbot that is responsible for guarding the chat against violations of the guardrails. \
You are given a summary of the guardrails and the user's question. \
You are to respond to the user's question and check if it violates the guardrails. \
If it does, you are to use the log_violation tool to log the violation. \
If it does not, you are to respond to the user's question with relevant answer from your knowledge." 
        system_prompt += f"\n\n## Guardrails:\n{self.guardrails}\n\n"
        system_prompt += f"With this context, please chat with the user, always keeping in mind the guardrails."

        return system_prompt
    
    def chat(self, message, history):
        messages = [{"role": "system", "content": self.system_prompt()}] + history + [{"role": "user", "content": message}]
        done = False
        while not done:
            response = self.gemini.chat.completions.create(model="gemini-2.5-flash", messages=messages, tools=tools)
            if response.choices[0].finish_reason=="tool_calls":
                message = response.choices[0].message
                tool_calls = message.tool_calls
                results = self.handle_tool_call(tool_calls)
                messages.append(message)
                messages.extend(results)
            else:
                done = True
        return response.choices[0].message.content
    

if __name__ == "__main__":
    chat_guard = ChatGuard()
    gr.ChatInterface(chat_guard.chat, type="messages").launch()
    