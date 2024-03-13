import os
import random
import hashlib
import streamlit as st
from langchain_pinecone import Pinecone as PineconeStore

#decorator
def enable_chat_history(func):
    if os.environ.get("OPENAI_API_KEY"):

        # to clear chat history after swtching chatbot
        current_page = func.__qualname__
        if "current_page" not in st.session_state:
            st.session_state["current_page"] = current_page
        if st.session_state["current_page"] != current_page:
            try:
                st.cache_resource.clear()
                del st.session_state["current_page"]
                del st.session_state["messages"]
            except:
                pass

        # to show chat history on ui
        if "messages" not in st.session_state:
            st.session_state["messages"] = [{"role": "assistant", "content": "How can I help you?"}]
        for msg in st.session_state["messages"]:
            st.chat_message(msg["role"]).write(msg["content"])

    def execute(*args, **kwargs):
        func(*args, **kwargs)
    return execute

def display_msg(msg, author):
    """Method to display message on the UI

    Args:
        msg (str): message to display
        author (str): author of the message -user/assistant
    """
    st.session_state.messages.append({"role": author, "content": msg})
    st.chat_message(author).write(msg)

def configure_openai_api_key():
    openai_api_key = ''
    os.environ['TOKENIZERS_PARALLELISM'] = 'False'
    if openai_api_key:
        st.session_state['OPENAI_API_KEY'] = openai_api_key
        os.environ['OPENAI_API_KEY'] = openai_api_key
    else:
        st.error("Please add your OpenAI API key to continue.")
        st.info("Obtain your key from this link: https://platform.openai.com/account/api-keys")
        st.stop()
    return openai_api_key

def configure_pinecone():
    pinecone_api_key = 'f3de1463-5a53-4862-a4ee-a6b6085758be'
    pinecone_store = PineconeStore(api_key=pinecone_api_key)

    if pinecone_api_key:
        st.session_state['PINECONE_API_KEY'] = pinecone_api_key
        os.environ['PINECONE_API_KEY'] = pinecone_api_key
    else:
        st.error("Please add your pinecone API key to continue.")
        st.info("Obtain your key from this link: https://docs.pinecone.io/docs/quickstart#2-get-your-api-key")
        st.stop()
    return pinecone_store

def configure_chroma():    
    return ''

def generate_uid(source):
    m = hashlib.md5()
    

    m.update(source.encode('utf-8'))
    uid = m.hexdigest()[:12]
    
    return uid