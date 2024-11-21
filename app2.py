import streamlit as st
import os

# import hw4 solution
from query_processor import QueryProcessor


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
                # create link to document
                doc_path = f"corpus/files/{doc_name}"
                st.markdown(
                    f"""
                    **{i}:** 
                    **Document:** [**{doc_name}**]({doc_path})  
                    **Score:** {score:.4f}  
                    **Matching Terms:** {', '.join(terms)}
                    """
                )
        else:
            st.warning("No matching documents found.")




if __name__ == "__main__":
    main()
