# Context tracking

def update_context(context, user_input):
    context.append(user_input)
    return context

def clear_context():
    import streamlit as st
    st.session_state.messages = []
    st.session_state.context = []
