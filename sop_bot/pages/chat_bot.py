import os
import utils
import streamlit as st
from streaming import StreamHandler
from sop_artifact import SopArtifactory
import time


st.set_page_config(page_title="ChatPDF", page_icon="📄")
st.header('Chat with your sops')
st.write('Has access to custom documents and can respond to user queries by referring to the content within those documents')


class CustomDataChatbot:

    def __init__(self):
        print('in chat bot init')
        if "artifact" not in st.session_state:
            print('no artifact defined')
            st.session_state['artifact'] = SopArtifactory()
        self.artifact = st.session_state['artifact']    
        print(self.artifact.qa_chain)
    

    @utils.enable_chat_history
    def main(self):       
        print('in chat bot main')
        if self.artifact.qa_chain is None:
            st.error('please upload files for context')                   
            
           
        user_query = st.chat_input(placeholder="Ask me anything!")

        if user_query:         
            print(self.artifact.qa_chain)
            utils.display_msg(user_query, 'user')

            with st.chat_message("assistant"):
                st_cb = StreamHandler(st.empty())
                response = self.artifact.qa_chain.run(user_query, callbacks=[st_cb])                            
                st.session_state.messages.append({"role": "assistant", "content": response})
                

if __name__ == "__main__":
    obj = CustomDataChatbot()
    obj.main()