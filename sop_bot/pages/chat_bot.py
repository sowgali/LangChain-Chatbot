import os
import utils
import streamlit as st
from streaming import StreamHandler
from sop_artifact import SopArtifactory
import time
import logging
logger = logging.getLogger('sop_bot')


st.set_page_config(page_title="ChatPDF", page_icon="📄")
st.header('Chat with your sops')
st.write('Has access to custom documents and can respond to user queries by referring to the content within those documents')


class CustomDataChatbot:

    def __init__(self):
        logger.debug('in chat bot init')
        if "artifact" not in st.session_state:
            logger.debug('no artifact defined')
            st.session_state['artifact'] = SopArtifactory()
        self.artifact = st.session_state['artifact']    
        logger.debug(self.artifact.qa_chain)
    

    @utils.enable_chat_history
    def main(self):       
        logger.debug('in chat bot main')
        # names = self.artifact.vectorDB.get_document_names()
        # with st.sidebar.expander(label='List of documents', expanded=True):
        #     for name, id in names.items():
        #         st.checkbox(label=f'{name}', key=f'{id}')
        
        user_query = st.chat_input(placeholder="Ask me anything!")

        if user_query:         
            logger.debug(self.artifact.qa_chain)
            utils.display_msg(user_query, 'user')

            with st.chat_message("assistant"):
                st_cb = StreamHandler(st.empty())
                response = self.artifact.qa_chain({"question":user_query}, callbacks=[st_cb])   
                with st.sidebar:
                    st.header('Source:')
                    st.text(response['source_documents'][0].metadata['source'][6:])                    
                st.session_state.messages.append({"role": "assistant", "content": response['answer']})
                

if __name__ == "__main__":
    obj = CustomDataChatbot()
    obj.main()