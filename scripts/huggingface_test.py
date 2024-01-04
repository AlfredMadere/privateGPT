import argparse
import os
import shutil
from typing import Optional

from llama_index import ServiceContext
from langchain.llms import OpenAI
from langchain_community.llms import HuggingFaceTextGenInference
import os
from llama_index.llms import ChatMessage
from transformers import AutoTokenizer
from llama_index.llms import LangChainLLM
HF_TOKEN: Optional[str] = os.getenv("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")


hf = HuggingFaceTextGenInference(
    inference_server_url="https://api-inference.huggingface.co/models/HuggingFaceH4/zephyr-7b-beta",
    max_new_tokens=512,
    top_k=10,
    top_p=0.95,
    typical_p=0.95,
    temperature=0.01,
    repetition_penalty=1.03,
)

def messages_to_prompt(messages: list[ChatMessage]) -> str:
        print("i'm in here")

        tokenizer = AutoTokenizer.from_pretrained("HuggingFaceH4/zephyr-7b-beta")
        formated_prompt = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
        print("formated_prompt", formated_prompt)
        return formated_prompt


def chat_with_zeph(messages: list[ChatMessage]):
  llm = LangChainLLM(llm=hf, messages_to_prompt=messages_to_prompt)
  response_gen = llm.stream_chat(messages=messages)
  return response_gen
    

def callHF(prompt: str):
   from llama_index.llms import HuggingFaceInferenceAPI, HuggingFaceTextGenInference
   llm = HuggingFaceInferenceAPI(model_name="HuggingFaceH4/zephyr-7b-alpha", token=HF_TOKEN)
  #  completion_response = llm.complete(prompt)
   service_context = ServiceContext.from_defaults(
            llm=llm
        )
  #  print(completion_response)

if __name__ == "__main__":
  #  callHF("once upon a")
  # messages  = [
  #   {"role": "system", "content": "Be precise and concise."},
  #   {"role": "user", "content": "Tell me 2 sentences about Perplexity."},
  # ]
  # chat_messages = [ChatMessage(content=m["content"], role=m["role"]) for m in messages]
  # response_gen = chat_with_zeph(chat_messages)
  # for delta in response_gen:
  #   print(delta.delta, end="")
  hf = HuggingFaceTextGenInference(
    inference_server_url="https://api-inference.huggingface.co/models/HuggingFaceH4/zephyr-7b-beta",
    max_new_tokens=512,
    top_k=10,
    top_p=0.95,
    typical_p=0.95,
    temperature=0.01,
    repetition_penalty=1.03,
  )

  def messages_to_prompt(messages: list[ChatMessage]) -> str:
          print("i'm in here")

          tokenizer = AutoTokenizer.from_pretrained("HuggingFaceH4/zephyr-7b-beta")
          formated_prompt = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
          print("formated_prompt", formated_prompt)
          return formated_prompt

  llm = LangChainLLM(llm=hf, messages_to_prompt=messages_to_prompt)

  messages  = [
      {"role": "system", "content": "Be precise and concise."},
      {"role": "user", "content": "Tell me 2 sentences about Perplexity."},
  ]
  chat_messages = [ChatMessage(content=m["content"], role=m["role"]) for m in messages]
  response_gen = llm.stream_chat(messages=chat_messages)
  for delta in response_gen:
      print(delta.delta, end="")