# -*- coding: utf-8 -*-
"""
Created on Thu Mar 21 16:12:00 2024

@author: kaiser
"""
import torch
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.core import Settings, Document
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader

Settings.embed_model = HuggingFaceEmbedding(
    model_name="BAAI/bge-small-en-v1.5"
)

# =============================================================================
# Settings.embed_model = HuggingFaceEmbedding(
#     model_name="models/e5_mistral_7b_instruct")
# =============================================================================


    

documents = SimpleDirectoryReader("raw_data").load_data(show_progress=True)
index = VectorStoreIndex.from_documents(documents, show_progress=True)

index.storage_context.persist(persist_dir="indexstorage2")

