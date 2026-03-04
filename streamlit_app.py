import streamlit as st
import sys
import os

# Add root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "")))

from src.phase4_generation.generator import NextLeapGenerator

st.set_page_config(page_title="NextLeap AI Advisor", page_icon="🎓", layout="centered")

# Custom CSS for NextLeap Blue theme
st.markdown("""
<style>
    .stApp {
        background-color: #0c111d;
        color: #f0f2f5;
    }
    .stTextInput > div > div > input {
        background-color: #1d2939;
        color: white;
        border: 1px solid #344054;
    }
    .stButton > button {
        background-color: #0066ff;
        color: white;
        border-radius: 8px;
        width: 100%;
    }
    .source-tag {
        background-color: #1d2939;
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 0.8em;
        margin-right: 5px;
    }
</style>
""", unsafe_allow_html=True)

st.title("🎓 NextLeap AI Advisor")
st.subheader("Your personal guide to NextLeap fellowships")

if "messages" not in st.session_state:
    st.session_state.messages = []

# Initialize Generator
@st.cache_resource
def get_generator():
    return NextLeapGenerator()

generator = get_generator()

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# User input
if prompt := st.chat_input("Ask about courses, fees, or curricula..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        response_placeholder = st.empty()
        full_response = ""
        sources = []
        
        # Use streaming for better experience
        for chunk in generator.generate_stream(prompt, history=st.session_state.messages[:-1]):
            if "|||[" in chunk:
                text, source_data = chunk.split("|||[")
                full_response += text
                sources = eval("[" + source_data) # Safe enough for this controlled stream
                response_placeholder.markdown(full_response)
            else:
                full_response += chunk
                response_placeholder.markdown(full_response + "▌")
        
        response_placeholder.markdown(full_response)
        
        if sources:
            st.markdown("---")
            st.markdown("**Sources:**")
            for src in set(sources):
                st.markdown(f"- [{src}]({src})")
                
    st.session_state.messages.append({"role": "assistant", "content": full_response})
