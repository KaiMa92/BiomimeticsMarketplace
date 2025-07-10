from ragpipeline.lib.indexing import NodeCreator, IndexManager
from ragpipeline.lib.load_models import load_openai_embedding, load_openai_llm
import pandas as pd
import uuid
import os

os.chdir('c:\\Users\\kaiser\\Documents\\BiomimeticsMarketplace')


class ScopusNodeCreator(NodeCreator):
     
    @classmethod
    def from_excel(cls, file_path: str, text_column: str):
        # Load the Excel file
        df = pd.read_excel(file_path, header = 0)

        # Ensure the text_column exists in the DataFrame
        if text_column not in df.columns:
            raise ValueError(f"Column '{text_column}' not found in the Excel file")

        # Check if 'id' column exists, if not, create one using uuid
        if 'doc_id' not in df.columns:
            df['doc_id'] = [str(uuid.uuid4()) for _ in range(len(df))]  # Generate unique UUIDs

            # Generate a new filename with metadata
        base_name = os.path.basename(file_path)
        file_name, file_extension = os.path.splitext(base_name)
        new_file_name = f"{file_name}{file_extension}"
        save_path = os.path.join(os.path.dirname(file_path), new_file_name)

        df.to_excel(save_path)
        # Create a dictionary with the 'id' column as the key and the text column as the value
        data_dct = {}
        for _, row in df.iterrows():
            # Use the 'id' column as the key instead of the index
            data_dct[row['doc_id']] = row[text_column]

        nodes = []
        for idx, text in data_dct.items():
            node = cls.get_nodes(text= text, id_ = str(idx))
            nodes += node
        return nodes



class ScopusIndexManager(IndexManager): 
    def __init__(self, index_path: str = None, metadata_path: str = None, embedding_model = load_openai_embedding('text-embedding-ada-002'), llm = load_openai_llm('gpt-4o')):
        """
        Initialize the BMMIndexManager.
        
        :param embedding_model: The embedding model to be used.
        :param index_path: Optional path from which to load an existing index.
        """   
        super().__init__(index_path, embedding_model = embedding_model, llm = llm)
        self.metadata_path = metadata_path
        self.metadata = None
        if self.metadata_path == None:
            pass
        else: 
            self.load_metadata(metadata_path)

    def load_metadata(self, metadata_path):
        self.metadata_path = metadata_path
        df = pd.read_excel(metadata_path, header = 0)
        df.set_index('doc_id', inplace=True)
        self.metadata = df
        return df
    
    def retrieve(self, query_text: str):
        """
        Retrieve nodes with scores from the retriever.
        
        :param query_text: The query string.
        :return: The retrieved nodes with scores.
        """
        if self.retriever is None:
            raise ValueError("Retriever is not set up. Please call setup_retriever first.")
        nodes = self.retriever.retrieve(query_text)

        new_retrieve_dct = {}
        for node in nodes:
            metadata_dct = self.metadata.loc[node.node.ref_doc_id].to_dict()
            retrieve_dct = {'score':node.score,
                            'text': node.node.text,
                            'start_char_idx': node.node.start_char_idx,
                            'end_char_idx': node.node.end_char_idx}
            combined_dct = {**metadata_dct, **retrieve_dct}
            new_retrieve_dct[node.node.node_id] = combined_dct
            retrieve_df = pd.DataFrame(new_retrieve_dct).T

        return retrieve_df

