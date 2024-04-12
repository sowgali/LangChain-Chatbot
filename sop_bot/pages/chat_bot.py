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

        names = self.artifact.vectorDB.get_document_names()
        with st.sidebar.expander(label='List of documents', expanded=True):
            # for name, id in names.items():
            #     st.checkbox(label=f'{name}', key=f'{id}')
            options = st.multiselect(label='Select Documents for Precise Context', options=names)
            if len(options) > 0:
                
                self.artifact.update_qa_chain(self.artifact.vectorDB.db, options)  

        # st.write('You selected:', options)

        
        user_query = st.chat_input(placeholder="Ask me anything!")

        if user_query:         
            logger.debug(self.artifact.qa_chain)
            utils.display_msg(user_query, 'user')

            with st.chat_message("assistant"):

                with st.spinner("Fetching results"):
                    st_cb = StreamHandler(st.empty())
                    response = self.artifact.qa_chain({"question":user_query}, callbacks=[st_cb])   
                    with st.sidebar:
                        st.header('Source:')
                        if response['source_documents'] and response['source_documents'][0].metadata['source']:
                            file_name = response['source_documents'][0].metadata['source'].split('/')[-1]
                            page_num = int(list(response['source_documents'][0])[1][1]['page']) + 1
                            url=self.artifact.get_s3_file(file_name=file_name, page_number=page_num)                           
                            st.text(file_name) 
                            #st.text(list(response['source_documents'][0])[1][1]['page'])
                            st.link_button("Go to file", url)
                        else:  
                            st.text('')                 
                    st.session_state.messages.append({"role": "assistant", "content": response['answer']})

                

if __name__ == "__main__":
    obj = CustomDataChatbot()
    obj.main()