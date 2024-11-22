import streamlit as st
import os
from flask import Flask, send_from_directory
from query_processor import QueryProcessor
from flask import Flask

app = Flask(__name__)

# serve static files from corpus/files dir
@app.route('/files/<path:filename>')
def serve_static_file(filename):
    return send_from_directory('corpus/files', filename)

def main():
    st.image("wizard-centered.png", use_container_width=False)
    st.markdown(
        """
        <h1 style="text-align: center;">THE ORACLE</h1>
        """,
        unsafe_allow_html=True,
    )
    st.markdown(
        """
        <p style="text-align: center;">
        Ask the Oracle anything, and he shall...provide related links.
        </p>
        """,
        unsafe_allow_html=True,
    )    
    # directory to output
    dict_path = os.path.join("output", "dict")
    post_path = os.path.join("output", "post")
    map_path = os.path.join("output", "map")

    try:
        processor = QueryProcessor(dict_path, post_path, map_path)
    except FileNotFoundError as e:
        st.error(f"Error: {e}")
        return

    # user search bar
    query = st.text_input(
        "",
        placeholder="Type your search query, and then press 'enter'...'",
    )

    # search on enter
    if query.strip():  # if query isn't blank
        with st.spinner("Processing your query..."):
            results = processor.process_query(query)

        # show results
        if results:
            st.success(f"Found {len(results)} matching documents.")
            for i, (doc_name, score, terms) in enumerate(results, start=1):
                # create URL to static file
                doc_url = f"/files/{doc_name}"
                st.markdown(
                    f"""
                    <p>
                    <b>{i}:</b><br>
                    <b>Document:</b> 
                    <a href="{doc_url}" target="_blank">{doc_name}</a><br>
                    <b>Score:</b> {score:.4f}<br>
                    <b>Matching Terms:</b> {', '.join(terms)}
                    </p>
                    """,
                    unsafe_allow_html=True,
                )
        else:
            st.warning("No matching documents found.")

if __name__ == "__main__":
    from streamlit.web.server import Server

    # add flask app to streamlit server
    server = Server.get_current()
    server._register_flask_endpoints(app)

    main()
