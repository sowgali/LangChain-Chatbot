import os
import utils
import streamlit as st
from streaming import StreamHandler
from sop_artifact import SopArtifactory
import time
import logging

logger = logging.getLogger("sop_bot")


st.set_page_config(page_title="ChatPDF", page_icon="📄")
st.header("Chat with your sops")
st.write(
    "Has access to custom documents and can respond to user queries by referring to the content within those documents"
)


class CustomDataChatbot:

    def __init__(self):
        logger.debug("in chat bot init")
        if "artifact" not in st.session_state:
            logger.debug("no artifact defined")
            st.session_state["artifact"] = SopArtifactory()
        self.artifact = st.session_state["artifact"]
        logger.debug(self.artifact.qa_chain)

    @utils.enable_chat_history
    def main(self):
        logger.debug("in chat bot main")

        names = self.artifact.vectorDB.get_document_names()
        if not names:
            st.write("No documents loaded yet!")
        print(names)

        # Input URL
        url = st.text_input("Enter URL:", placeholder="https://example.com")
        if st.button("Process"):
            if url:
                try:
                    st.write("Fetching content...")
                    result = self.artifact.upload_urls(url)

                    st.success("Processing completed!")
                    # st.write(result)
                except Exception as e:
                    st.error(f"Error processing the URL: {e}")
            else:
                st.warning("Please enter a valid URL.")
        # with st.sidebar.expander(label="List of documents", expanded=True):
        #     # for name, id in names.items():
        #     #     st.checkbox(label=f'{name}', key=f'{id}')
        #     options = st.multiselect(
        #         label="Select Documents for Precise Context", options=names
        #     )
        #     if len(options) > 0:

        #         self.artifact.update_qa_chain(self.artifact.vectorDB.db, options)

        # st.write('You selected:', options)

        user_query = st.chat_input(placeholder="Ask me anything!")

        if user_query:
            logger.debug(self.artifact.qa_chain)
            utils.display_msg(user_query, "user")

            with st.chat_message("assistant"):

                with st.spinner("Fetching results"):
                    st_cb = StreamHandler(st.empty())
                    response = self.artifact.qa_chain(
                        {"question": user_query}, callbacks=[st_cb]
                    )
                    print(response)
                    with st.sidebar:
                        st.header("Source:")
                        file_name = ""
                        page_num = 0
                        if (
                            response["source_documents"]
                            and response["source_documents"][0].metadata["source"]
                        ):
                            url = response["source_documents"][0].metadata["source"]
                            # for doc in response['source_documents']:
                            #     print(f'page content of the doc is : --------  {doc.page_content}')
                            #     if response['answer'] in doc.page_content:
                            #         file_name = doc.metadata['source'].split('/')[-1]
                            #         page_num = int(list(doc)[1][1]['page']) + 1
                            # if file_name is "":
                            #     file_name = (
                            #         response["source_documents"][0]
                            #         .metadata["source"]
                            #         .split("/")[-1]
                            #     )
                            #     page_num = (
                            #         int(
                            #             list(response["source_documents"][0])[1][1][
                            #                 "page"
                            #             ]
                            #         )
                            #         + 1
                            #     )

                            # print(response)
                            # url = self.artifact.get_s3_file(
                            #     file_name=file_name, page_number=page_num
                            # )
                            # st.text(file_name)
                            # # st.text(list(response['source_documents'][0])[1][1]['page'])
                            st.link_button("Go to file", url)
                        else:
                            st.text("")
                    st.session_state.messages.append(
                        {"role": "assistant", "content": response["answer"]}
                    )


if __name__ == "__main__":
    obj = CustomDataChatbot()
    obj.main()
