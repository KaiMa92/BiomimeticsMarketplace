# -*- coding: utf-8 -*-
"""
Created on Mon Mar 25 14:10:48 2024

@author: kaiser
"""
import torch
from llama_index.llms.huggingface import HuggingFaceLLM
#from IPython.display import Markdown, display
from llama_index.core import PromptTemplate
from transformers import BitsAndBytesConfig



SYSTEM_PROMPT = """You are an AI assistant that answers questions in a friendly manner, based on the given source documents. Here are some rules you always follow:
- Generate human readable output, avoid creating output with gibberish text.
- Generate only the requested output.
- Never say thank you, that you are happy to help, Say that you are IVWs AI agent and then juust answer directly.
- Generate professional language typically used in business documents in North America.
"""

query_wrapper_prompt = PromptTemplate(
    "[INST]<<SYS>>\n" + SYSTEM_PROMPT + "<</SYS>>\n\n{query_str}[/INST] "
)

quantization_config = BitsAndBytesConfig(load_in_8bit=True,
                                         llm_int8_threshold=200.0)

selected_model = "models/mistral_7B_Instruct_v02" #model directory
llm = HuggingFaceLLM(
    context_window=4048,#4048 WARNING:llama_index.llms.huggingface.base:Supplied context_window 4048 is greater than the model's max input size 2048. Disable this warning by setting a lower context_window.
    max_new_tokens=2048,
    tokenizer_name=selected_model,
    model_name=selected_model,
    device_map="auto",
    quantization_config=quantization_config,
    query_wrapper_prompt=query_wrapper_prompt,
    generate_kwargs={"temperature": 0.0, "do_sample": False},
    model_kwargs={"torch_dtype": torch.float16, "load_in_8bit":True})

from llama_index.embeddings.huggingface import HuggingFaceEmbedding
embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-small-en-v1.5")

from llama_index.core import Settings
Settings.llm = llm
Settings.embed_model = embed_model


from llama_index.core import StorageContext, load_index_from_storage
# rebuild storage context
storage_context = StorageContext.from_defaults(persist_dir="indexstorage")
# load index
index = load_index_from_storage(storage_context, embed_model=HuggingFaceEmbedding(model_name="BAAI/bge-small-en-v1.5"), show_progress=True)
# set Logging to DEBUG for more detailed outputs
query_engine = index.as_query_engine(streaming=False, similarity_top_k=3)
#response = query_engine.query("What kind of experiments were carried out?")

def chat(query):
    #set streaming to False
    response = query_engine.query(query)
    print(response.response)
    print('Sources:')
    for v in response.metadata.values():
        print(v['file_name']+' page '+ v['page_label'])


def stream_answer(query):
    #set streaming to True
    streaming_response = query_engine.query(query)
    for text in streaming_response.response_gen:
        print(text,end = '')
    print('\n Sources:')
    for v in streaming_response.metadata.values():
        print(v['file_name']+' page '+ v['page_label'])
#display(Markdown(f"{response}"))