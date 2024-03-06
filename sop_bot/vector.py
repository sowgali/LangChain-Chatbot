from abc import abstractmethod, ABC
from langchain.vectorstores import DocArrayInMemorySearch
from langchain_pinecone import Pinecone as PineconeStore
from langchain.vectorstores import Chroma
from langchain.embeddings import HuggingFaceEmbeddings

import utils
import os
import chromadb
import logging
logger = logging.getLogger('sop_bot')

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
    @abstractmethod
    def get_documents(self, persist_directory= None):
        pass
    @abstractmethod
    def is_document_exist(self, document_name, persist_directory=None):    
        pass
    @abstractmethod
    def delete_document(self, document_name, persist_directory=None):    
        pass
        
    def load_documents(self, ids, splits, embeddings, persist_directory):
        pass


class ChromaDB(VectorDB):
    def __init__(self, name, index_name='sop-chat'):
        self.name = name
        self.index_name = index_name
        self.retriever = None    
        self.client = None
        self.db = Chroma(persist_directory=name, embedding_function=HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2"))
        

    def insert_vector(self, vector):
        # Implementation specific to Chromed
        logger.debug("Inserting vector into Chromed:", vector)

    def query_vector(self, vector):
        # Implementation specific to Chromed
        logger.debug("Querying vector from Chromed:", vector)
        
    def from_documents(self, splits, embeddings):  
        logger.debug(f'in from_documents with persisten dir : {self.name}')      
        chroma_db = Chroma.from_documents(documents=splits, embedding = embeddings, persist_directory=self.name, client=self.client)
        chroma_db.persist()
        self.db = chroma_db
        retriever = chroma_db.as_retriever(
            search_type='mmr',
            search_kwargs={'k':2, 'fetch_k':4}
        )
        return chroma_db    
      
        
    def get_retreiver(self,  embeddings):
        self.client = chromadb.PersistentClient()
        chroma_db = Chroma(embedding = embeddings, persist_directory=self.name, client=self.client, collection='sop_chat')
        chroma_db.persist()
        retriever = chroma_db.as_retriever(
            search_type='mmr',
            search_kwargs={'k':2, 'fetch_k':4}
        )
        return retriever    
    
    def get_documents(self, persist_directory= None):
        if persist_directory is None:
            persist_directory = self.name
        logger.debug(f'in get_documents with persisten dir : {persist_directory}')
        document_name =   "./tmp/PadmaAwardees2024.pdf"  
        source_string =  "{0}".format(document_name)  
        logger.debug(source_string)
        if self.db is None:
            self.db = Chroma(persist_directory=persist_directory)
        db = self.db
        db_records = db.get(where={"source":document_name})
        #db_records = Chroma(persist_directory='chroma_db').get(where={"source": "./tmp/PadmaAwardees2024.pdf"})
        logger.debug(db_records['metadatas'])          
        
        logger.debug(f"length of ids in db {len(db_records['ids'])}")
        
    
    def is_document_exist(self, document_name, persist_directory=None):    
        if persist_directory is None:
            persist_directory = self.name
        logger.debug(f'in is_document_exist with persisten dir : {persist_directory}')
        source_string =  "{0}".format(document_name) 
        logger.debug(f'source string verifying is {source_string}') 
        if self.db is None:
                self.db = Chroma(persist_directory=persist_directory)
        db = self.db
        db_records = db.get(where={"source":document_name})
        logger.debug(db_records['metadatas'])  
        logger.debug(f"db ids returned are {db_records['ids']}")
        if len(db_records['ids']) > 0:
            return True
        
        return False
        
        
    
    def delete_document(self, document_name, persist_directory=None):    
        if persist_directory is None:
            persist_directory = self.name
        logger.debug(f'in delete_document with persisten dir : {persist_directory}')
        source_string =  "{0}".format(document_name) 
        db = Chroma(persist_directory=persist_directory)
        if self.db is None:
            self.db = Chroma(persist_directory=persist_directory)
        db = self.db
        db_records = db.get(where={"source":document_name})
        logger.debug(db_records['metadatas'])  
        
        ids_to_del = []
        logger.debug(f"total records in the collection for the source {document_name} are {len(db_records['ids'])}")
        for idx in range(len(db_records['ids'])):

            id = db_records['ids'][idx]
            metadata = db_records['metadatas'][idx]

            if metadata['source'] == document_name:
                ids_to_del.append(id)
        logger.debug(len(ids_to_del))
        db._collection.delete(ids_to_del)
        db_records = Chroma(persist_directory=persist_directory).get(source_string)
        logger.debug(f"total records in the collection after deletion for the source {document_name} are {len(db_records['ids'])}")
        
    def load_documents(self, ids, splits, embeddings, persist_directory):
        client = chromadb.PersistentClient(persist_directory)
        collection = client.get_or_create_collection(self.index_name)
        for id in ids:
            logger.debug(id, end='\n')
        for doc in splits:
            logger.debug(doc, end='\n')
        logger.debug(f"ids length: {len(ids)} and docs count is : {len(splits)}")
        collection.add(ids=ids, documents=splits,embeddings=embeddings)
        return collection
        
        


class Pinecone(VectorDB):
    def __init__(self, name, index_name='sop-chat'):
        self.name = name
        self.index_name = index_name
        self.pinecone_store = utils.configure_pinecone()
        self.retriever = None  

    def insert_vector(self, vector):
        # Implementation specific to Pinecone
        logger.debug("Inserting vector into Pinecone:", vector)

    def query_vector(self, vector):
        # Implementation specific to Pinecone
        logger.debug("Querying vector from Pinecone:", vector)
        
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
        logger.debug("Inserting vector into Pinecone:", vector)

    def query_vector(self, vector):
        # Implementation specific to Pinecone
        logger.debug("Querying vector from Pinecone:", vector)
        
    def from_documents(self, splits, embeddings):
        return DocArrayInMemorySearch.from_documents(splits, embeddings)

    
