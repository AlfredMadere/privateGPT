import argparse
import os
import shutil
from typing import Optional

from llama_index import ServiceContext
from llama_index.llms import LangChainLLM
HF_TOKEN: Optional[str] = os.getenv("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")


def callHF(prompt: str):
   from llama_index.llms import HuggingFaceInferenceAPI, HuggingFaceTextGenInference
   llm = HuggingFaceInferenceAPI(model_name="HuggingFaceH4/zephyr-7b-alpha", token=HF_TOKEN)
  #  completion_response = llm.complete(prompt)
   service_context = ServiceContext.from_defaults(
            llm=llm
        )
  #  print(completion_response)

if __name__ == "__main__":
   callHF("once upon a")
