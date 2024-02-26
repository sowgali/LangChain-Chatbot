from abc import abstractmethod, ABC
from langchain.vectorstores import DocArrayInMemorySearch
from langchain_pinecone import Pinecone as PineconeStore
from langchain.vectorstores import Chroma
import utils
import os

SCRIPT_PATH: str = os.path.dirname(os.path.abspath(__file__))


class VectorDB:
    def __init__(self, name, index_name='sop-chat'):
        self.name = name
        self.index_name = index_name
        self.retriever = None  

    def insert_vector(self, vector):
        raise NotImplementedError("Subclasses must implement insert_vector method")

    def query_vector(self, vector):
        raise NotImplementedError("Subclasses must implement query_vector method")
    
    @abstractmethod
    def from_documents(self, splits, embeddings):
        pass


class ChromaDB(VectorDB):
    def __init__(self, name, index_name='sop-chat'):
        self.name = name
        self.index_name = index_name
        self.retriever = None        

    def insert_vector(self, vector):
        # Implementation specific to Chromed
        print("Inserting vector into Chromed:", vector)

    def query_vector(self, vector):
        # Implementation specific to Chromed
        print("Querying vector from Chromed:", vector)
        
    def from_documents(self, splits, embeddings):
        chroma_db = Chroma.from_documents(documents=splits, embedding = embeddings, persist_directory='chroma_db')
        chroma_db.persist()
        self.retriever = chroma_db.as_retriever(
            search_type='mmr',
            search_kwargs={'k':2, 'fetch_k':4}
        )
        return chroma_db     
        



class Pinecone(VectorDB):
    def __init__(self, name, index_name='sop-chat'):
        self.name = name
        self.index_name = index_name
        self.pinecone_store = utils.configure_pinecone()
        self.retriever = None  

    def insert_vector(self, vector):
        # Implementation specific to Pinecone
        print("Inserting vector into Pinecone:", vector)

    def query_vector(self, vector):
        # Implementation specific to Pinecone
        print("Querying vector from Pinecone:", vector)
        
    def from_documents(self, splits, embeddings):
        docsearch = self.pinecone_store.from_documents(splits, embeddings, index_name=self.index_name)
        retriever = PineconeHybridSearchRetriever(
                    embeddings=embed, sparse_encoder=bm25, index=index, top_k= int(5), alpha= float(0.7))
        return docsearch    
    


class InmemoryDB(VectorDB):
    def __init__(self, name, index_name='sop-chat'):
        self.name = name
        self.index_name = index_name
        self.retriever = None  

    def insert_vector(self, vector):
        # Implementation specific to Pinecone
        print("Inserting vector into Pinecone:", vector)

    def query_vector(self, vector):
        # Implementation specific to Pinecone
        print("Querying vector from Pinecone:", vector)
        
    def from_documents(self, splits, embeddings):
        return DocArrayInMemorySearch.from_documents(splits, embeddings)

    
