import os
import utils
import streamlit as st
from streaming import StreamHandler
from vector import InmemoryDB, ChromaDB

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
        self.vectorDB = ChromaDB('chroma_db')
        self.qa_chain = None

    def save_file(self, file):
        folder = 'tmp'
        if not os.path.exists(folder):
            os.makedirs(folder)
        
        file_path = f'./{folder}/{file.name}'
        with open(file_path, 'wb') as f:
            f.write(file.getvalue())
        return file_path    
    
    def upload_files(self, uploaded_files):
        # Load documents
        docs = []
        for file in uploaded_files:
            file_path = self.save_file(file)
            print(f"file type is {file.type}")
            if file.type == "application/pdf":
                print('in pdf loader')
                loader = PyPDFLoader(file_path)
            else:
                print('in doc loader')
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
    
    
    def setup_qa_chain(self, retriever):       
        print('setting up qa_chain')
        
        
        # Setup memory for contextual conversation        
        memory = ConversationBufferMemory(
            memory_key='chat_history',
            return_messages=True
        )

        # Setup LLM and QA chain
        llm = ChatOpenAI(model_name=self.openai_model, temperature=0, streaming=True)
        qa_chain = ConversationalRetrievalChain.from_llm(llm, retriever=retriever, memory=memory, verbose=True)
        return qa_chain

   