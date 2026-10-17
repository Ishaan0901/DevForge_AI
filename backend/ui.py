import streamlit as st
import requests
import streamlit.components.v1 as components

st.title("DevForge AI")
st.write("Describe a Python program or a website and I will build it.")

query = st.text_area(
    "Your request",
    placeholder="Create a program that prints numbers 1 to 5",
)

if st.button("Generate"):
    if not query.strip():
        st.warning("Please enter a request.")
    else:
        with st.spinner("Working on it..."):
            try:
                res = requests.post(
                    "http://localhost:8000/generate",
                    json={"query": query},
                    timeout=180,
                )
                data = res.json()
            except Exception as e:
                st.error(f"Could not reach the API: {e}")
                st.stop()

        if "error" in data:
            st.error(data["error"])

        elif data["type"] == "website":
            tab1, tab2 = st.tabs(["Preview", "Code"])
            with tab1:
                components.html(data["html"], height=600, scrolling=True)
            with tab2:
                st.code(data["html"], language="html")
            st.download_button(
                "Download index.html",
                data["html"],
                file_name="index.html",
                mime="text/html",
            )

        else:
            st.subheader("generated_code.py")
            st.code(data["code"], language="python")
            st.subheader("Output")
            st.code(data["output"] or "(no output)")
            if data["error"]:
                st.subheader("Errors")
                st.code(data["error"])