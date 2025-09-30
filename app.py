import streamlit as st
from loadfinbertmodel import tokenizer, model
import torch

st.set_page_config(page_title="LLM Chat", layout="wide")

st.title("💬 LLM Chat")

user_input = st.text_input("You:", "")

if st.button("Send") and user_input:
    inputs = tokenizer(user_input, return_tensors="pt")
    outputs = model.generate(
        **inputs,
        max_new_tokens=50,
        do_sample=True,
        top_k=50,
        top_p=0.95,
        temperature=0.8
    )
    response = tokenizer.decode(outputs[0], skip_special_tokens=True)
    st.markdown(f"**Model:** {response}")
