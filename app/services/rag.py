from ragpipeline.lib.indexing import NodeCreator, IndexManager
from ragpipeline.lib.chunking import sentence_splitter, token_splitter
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
    def __init__(self, index_path: str = None, metadata_path: str = None, embedding_model = load_openai_embedding('text-embedding-3-small'), llm = load_openai_llm('gpt-4o')):
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

        return new_retrieve_dct

e_model = 'text-embedding-ada-002'
xcel = 'datasets\Scopus_Senckenberg_ada\Senckenberg_Paper.xlsx'
i_path = 'datasets\Scopus_Senckenberg_ada\index'

# =============================================================================
# ScopusNodeCreator.initialize(token_splitter(1024, 20))
# nodes = ScopusNodeCreator.from_excel(xcel, 'Abstract')
# sim = ScopusIndexManager(embedding_model=load_openai_embedding(e_model))
# sim.create_from_nodes(nodes)
# sim.store(i_path)
# =============================================================================
sim = ScopusIndexManager(index_path = i_path, metadata_path= xcel, embedding_model=load_openai_embedding(e_model))
sim.setup_retriever(top_k = 10)
#retrieved = sim.retrieve('load transfer between materials with different stiffness.')

# =============================================================================
# df = pd.DataFrame(r_dct).T
# awa = df['Authors with affiliations']['04fdefb4-5acd-48ac-a360-dfde097954ec'].split(';')
# frankfurt_authors_idx = [i for i,awa in enumerate(awas) if 'Frankfurt' in awa]
# authors_fullname_lst = df['Author full names']['04fdefb4-5acd-48ac-a360-dfde097954ec'].split(';')
# frankfurt_authors = [authors_fullname_idx[index] for index in frankfurt_authors_lst]
# =============================================================================



def add_frankfurt_authors_column(df):
    # Initialize an empty list to store the Frankfurt authors for each row
    frankfurt_authors_column = []

    # Loop through each row of the dataframe
    for index, row in df.iterrows():
        # Extract the affiliations and full names for the current row
        awa = row['Authors with affiliations'].split(';')
        authors_fullname_lst = row['Author full names'].split(';')

        # List comprehension to find the indices of Frankfurt authors
        frankfurt_authors_idx = [i for i, awa in enumerate(awa) if 'Frankfurt' in awa]

        # Create the Frankfurt authors list using indices
        frankfurt_authors = [authors_fullname_lst[index] for index in frankfurt_authors_idx]

        # Join the Frankfurt authors into a single string and append to the list
        frankfurt_authors_column.append('; '.join(frankfurt_authors))

    # Add the Frankfurt authors as a new column in the dataframe
    df['Frankfurt authors'] = frankfurt_authors_column

    return df

def author_ranking_with_score_and_count_cleaned(df, author_column, score_column):
    # Create a dataframe with authors and corresponding scores
    authors_scores = df[[author_column, score_column]].copy()

    # Split authors by ';' and explode the rows, then reset index to avoid duplicate labels
    authors_scores = authors_scores.explode(author_column).reset_index(drop=True)

    # Remove rows where the author is None or empty
    authors_scores = authors_scores[authors_scores[author_column].notna() & (authors_scores[author_column] != '')]

    # Group by author, summing scores and counting occurrences
    author_rank = authors_scores.groupby(author_column).agg(
        total_score=(score_column, 'sum'),
        count=(score_column, 'size')
    ).sort_values(by='total_score', ascending=False)

    return author_rank



