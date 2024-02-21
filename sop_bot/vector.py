from abc import abstractmethod, ABC
from langchain.vectorstores import DocArrayInMemorySearch
from langchain_pinecone import Pinecone as PineconeStore
from langchain.vectorstores import Chroma
import utils


class VectorDB:
    def __init__(self, name, index_name='sop-chat'):
        self.name = name
        self.index_name = index_name

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

    def insert_vector(self, vector):
        # Implementation specific to Chromed
        print("Inserting vector into Chromed:", vector)

    def query_vector(self, vector):
        # Implementation specific to Chromed
        print("Querying vector from Chromed:", vector)
        
    def from_documents(self, splits, embeddings):
        chroma_db = Chroma.from_documents(documents=splits, embedding = embeddings, persist_directory='chroma_db')
        chroma_db.persist()
        return chroma_db
        



class Pinecone(VectorDB):
    def __init__(self, name, index_name='sop-chat'):
        self.name = name
        self.index_name = index_name
        self.pinecone_store = utils.configure_pinecone()

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

    def insert_vector(self, vector):
        # Implementation specific to Pinecone
        print("Inserting vector into Pinecone:", vector)

    def query_vector(self, vector):
        # Implementation specific to Pinecone
        print("Querying vector from Pinecone:", vector)
        
    def from_documents(self, splits, embeddings):
        return DocArrayInMemorySearch.from_documents(splits, embeddings)

    
