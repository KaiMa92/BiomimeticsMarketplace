from ragpipeline.lib.indexing import NodeCreator, IndexManager
from ragpipeline.lib.chunking import SentenceSplitter
from ragpipeline.lib.load_models import load_openai_embedding
import pandas as pd

splitter = SentenceSplitter()
NodeCreator.initialize(splitter)
im = IndexManager()

def load_data_from_excel(file_path: str, text_column: str):
    # Load the Excel file
    df = pd.read_excel(file_path)

    # Ensure the text_column exists in the DataFrame
    if text_column not in df.columns:
        raise ValueError(f"Column '{text_column}' not found in the Excel file")

    # Create a dictionary with the index as the key and the text column as the value
    data_dct = {}
    for idx, row in df.iterrows():
        text = row[text_column]
        data_dct[idx] = text

    return data_dct

file_path = '\datasets\Scopus_Senckenberg\Senckenberg_Paper.xlsx"'
text_column = 'Abstract'
store_dir = '\datasets\Scopus_Senckenberg\index'

data_dct = load_data_from_excel(file_path, text_column)
nodes = []
for idx, text in data_dct.items():
    node = NodeCreator.get_nodes(text= text, id_ = idx)
    nodes += node

embedding_model = load_openai_embedding('text-embedding-3-large')
im.create_from_nodes(nodes, embedding_model)
im.store(store_dir)

im.load(store_dir)
im.setup_retriever(top_k = 10)



