# app.py
import streamlit as st
from langchain_core.messages import HumanMessage
from agent import appointment_agent

st.title("Google Calendar Booking Assistant")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("How can I help you book an appointment?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Process with agent
    result = appointment_agent.invoke({
        "messages": [HumanMessage(content=prompt)],
        "user_intent": "",
        "appointment_details": {}
    })
    
    response = result["messages"][-1].content
    st.session_state.messages.append({"role": "assistant", "content": response})
    with st.chat_message("assistant"):
        st.markdown(response)