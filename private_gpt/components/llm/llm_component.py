import logging
from typing import Optional

from injector import inject, singleton
from llama_index import set_global_tokenizer
from llama_index.llms import MockLLM
from llama_index.llms import LLM
from transformers import AutoTokenizer  # type: ignore

from private_gpt.components.llm.prompt_helper import get_prompt_style
from private_gpt.paths import models_cache_path, models_path
from private_gpt.settings.settings import Settings
import os
from langchain_community.llms import HuggingFaceTextGenInference
from llama_index.llms import LangChainLLM
from llama_index.llms import ChatMessage


logger = logging.getLogger(__name__)

@singleton
class LLMComponent:
    llm: LLM

    @inject
    def __init__(self, settings: Settings) -> None:
        llm_mode = settings.llm.mode
        if settings.llm.tokenizer:
            set_global_tokenizer(
                AutoTokenizer.from_pretrained(
                    pretrained_model_name_or_path=settings.llm.tokenizer,
                    cache_dir=str(models_cache_path),
                )
            )

        logger.info("Initializing the LLM in mode=%s", llm_mode)
        match settings.llm.mode:
            case "local":
                from llama_index.llms import LlamaCPP

                prompt_style = get_prompt_style(settings.local.prompt_style)

                self.llm = LlamaCPP(
                    model_path=str(models_path / settings.local.llm_hf_model_file),
                    temperature=0.1,
                    max_new_tokens=settings.llm.max_new_tokens,
                    context_window=settings.llm.context_window,
                    generate_kwargs={},
                    # All to GPU
                    model_kwargs={"n_gpu_layers": -1},
                    # transform inputs into Llama2 format
                    messages_to_prompt=prompt_style.messages_to_prompt,
                    completion_to_prompt=prompt_style.completion_to_prompt,
                    verbose=True,
                )

            case "sagemaker":
                from private_gpt.components.llm.custom.sagemaker import SagemakerLLM

                self.llm = SagemakerLLM(
                    endpoint_name=settings.sagemaker.llm_endpoint_name,
                    max_new_tokens=settings.llm.max_new_tokens,
                    context_window=settings.llm.context_window,
                )
            case "openai":
                from llama_index.llms import OpenAI

                openai_settings = settings.openai
                self.llm = OpenAI(
                    api_base=openai_settings.api_base,
                    api_key=openai_settings.api_key,
                    model=openai_settings.model,
                )
            case "openailike":
                from llama_index.llms import OpenAILike

                openai_settings = settings.openai
                self.llm = OpenAILike(
                    api_base=openai_settings.api_base,
                    api_key=openai_settings.api_key,
                    model=openai_settings.model,
                    is_chat_model=True,
                    max_tokens=None,
                    api_version="",
                )
            case "huggingface":  
                #FIXME: clean up and abstract this so that messages_to_prompt comes from something like the following
                """
                    prompt_style = get_prompt_style(settings.local.prompt_style)
                    messages_to_prompt=prompt_style.messages_to_prompt
                """
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
                    tokenizer = AutoTokenizer.from_pretrained("HuggingFaceH4/zephyr-7b-beta")
                    formated_prompt = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
                    print(formated_prompt)
                    return formated_prompt
                
                self.llm = LangChainLLM(llm=hf, messages_to_prompt=messages_to_prompt)
                # , messages_to_prompt=messages_to_prompt
                # self.llm = MockLLM()
            case "mock":
                self.llm = MockLLM()
