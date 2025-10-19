import streamlit as st

st.set_page_config(
    page_title="Test App",
    page_icon="🧪",
    layout="wide"
)

st.title("🧪 Test Application")
st.write("This is a simple test to verify Streamlit is working correctly.")

if st.button("Test Button"):
    st.success("Button clicked successfully!")

st.write("If you can see this text, Streamlit is working properly.")
