import os
import utils
import streamlit as st
from streaming import StreamHandler
from sop_artifact import SopArtifactory

st.set_page_config(page_title="LoadPDF", page_icon="📄")
st.header('Load your sops')
st.write('Has access to custom documents and can respond to user queries by referring to the content within those documents')


class CustomDataLoader:

    def __init__(self):
        print('in data loader init')
        if "artifact" not in st.session_state:
            print('no artifact defined in data loader')
            st.session_state['artifact'] = SopArtifactory()
        self.artifact = st.session_state['artifact']    
        print(self.artifact.qa_chain)
    
    @st.spinner('processing request..')
    def upload_files(self, uploaded_files):
        # Load documents
       self.artifact.upload_files(uploaded_files)           

    
    def main(self):
        print('in data loader main')
        # User Inputs
        uploaded_files = st.sidebar.file_uploader(label='Upload PDF files', type=['pdf'], accept_multiple_files=True)

        
        if uploaded_files:
            self.artifact.upload_files(uploaded_files=uploaded_files)
            st.success('file got uploaded successfully', icon=None)
            

       

if __name__ == "__main__":
    obj = CustomDataLoader()
    obj.main()