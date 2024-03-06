import os
import utils
import streamlit as st
from streaming import StreamHandler
from vector import InmemoryDB, ChromaDB
import logging
logger = logging.getLogger('sop_bot')
logger.setLevel(level=logging.DEBUG)

from langchain.chat_models import ChatOpenAI
from langchain.document_loaders import PyPDFLoader, Docx2txtLoader
from langchain.memory import ConversationBufferMemory
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.chains import ConversationalRetrievalChain
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.prompts import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    MessagesPlaceholder,
)
from langchain_core.messages import SystemMessage


class SopArtifactory:

    def __init__(self):
        utils.configure_openai_api_key()        
        self.openai_model = "gpt-3.5-turbo"       
        self.vectorDB = ChromaDB('test_chroma_db')
        self.qa_chain = self.setup_qa_chain(self.vectorDB.db)       

    def save_file(self, file):
        folder = 'tmp'
        if not os.path.exists(folder):
            os.makedirs(folder)
        
        file_path = f'./{folder}/{file.name}'
        if self.vectorDB.is_document_exist(file_path):
            logger.debug(f'document {file.name} already exists in vector db, so deleting it and updating')
            self.vectorDB.delete_document(file_path)
        else:
            logger.debug(f'document {file.name} doesnt exist anymore so just loading it')
        with open(file_path, 'wb') as f:
            f.write(file.getvalue())
        return file_path    
    
    def upload_files(self, uploaded_files):
        # Load documents
        docs = []
        for file in uploaded_files:
            file_path = self.save_file(file)
            logger.debug(f"file type is {file.type}")
            if file.type == "application/pdf":
                logger.debug('in pdf loader')
                loader = PyPDFLoader(file_path)
            else:
                logger.debug('in doc loader')
                loader = Docx2txtLoader(file_path)
            docs.extend(loader.load())
        
        # Split documents
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1500,
            chunk_overlap=200
        )
        splits = text_splitter.split_documents(docs)

        # Create embeddings and store in vectordb
        embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        vectordb = self.vectorDB.from_documents(splits, embeddings)

        # Define retriever
        retriever = vectordb.as_retriever(
            search_type='mmr',
            search_kwargs={'k':2, 'fetch_k':4}
        )        
       
        
        memory = ConversationBufferMemory(
            memory_key='chat_history',
            return_messages=True,
            output_key='answer'
        )

        # Setup LLM and QA chain
        llm = ChatOpenAI(model_name=self.openai_model, temperature=0, streaming=True)
        self.qa_chain = ConversationalRetrievalChain.from_llm(llm, retriever=retriever, memory=memory, verbose=True, rephrase_question=False,
                                        get_chat_history=lambda h : h,
                                        return_source_documents=True)
        return self.qa_chain 
    
    
    def setup_qa_chain(self, vectordb):       
        logger.debug('setting up qa_chain')
        
        # Define retriever
        retriever = vectordb.as_retriever(
            search_type='mmr',
            search_kwargs={'k':2, 'fetch_k':4}
        ) 
        
        
        memory = ConversationBufferMemory(
            memory_key='chat_history',
            return_messages=True,
            output_key='answer'
        )

        # Setup LLM and QA chain
        llm = ChatOpenAI(model_name=self.openai_model, temperature=0, streaming=True)
        self.qa_chain = ConversationalRetrievalChain.from_llm(llm, retriever=retriever, memory=memory, verbose=True, rephrase_question=False,
                                        get_chat_history=lambda h : h,
                                        return_source_documents=True)
        return self.qa_chain 

   