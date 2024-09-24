import streamlit as st

from python_streaming.chat_client import consume_chat_response


with st.chat_message("assistant"):
    st.write(
        "Hello! 👋 "
        "I'm some AI assistant, here to demonstrate how simple it is to stream responses. "
        "Please ask away!"
    )

user_input = st.chat_input("Ask something...")
if user_input:
    with st.chat_message("user"):
        st.write(user_input)
    with st.chat_message("assistant"):
        response = st.write_stream(consume_chat_response(user_input))
