import streamlit as st
import pandas as pd
import sys
from utils.peek import ChromaPeek

# Parse command-line arguments
# Streamlit passes arguments after '--' in sys.argv
def get_cli_path():
    """Extract --path argument from command line."""
    if '--path' in sys.argv:
        idx = sys.argv.index('--path')
        if idx + 1 < len(sys.argv):
            return sys.argv[idx + 1]
    return None

cli_path = get_cli_path()

st.set_page_config(page_title="chroma-peek", page_icon="👀")

## styles ##
padding = 100
st.markdown(""" <style>
            #MainMenu {
                visibility: hidden;
            }
            footer {
                visibility: hidden;
            }
            </style> """, 
            unsafe_allow_html=True)
############

st.title("Chroma Peek 👀")

# Initialize session state for path
if 'chroma_path' not in st.session_state:
    # Use command-line argument if provided, otherwise empty string
    st.session_state.chroma_path = cli_path if cli_path else ""

# get uri of the persist directory
col1, col2 = st.columns([4,1])  # adjust the ratio as needed
with col1:
    path = st.text_input(
        "Enter persist path", 
        value=st.session_state.chroma_path,
        placeholder="paste full path of persist",
        key="chroma_path"
    )
with col2:
    st.write("") 
    if st.button('🔄'):
        st.rerun()

st.divider()

# load collections
if st.session_state.chroma_path and st.session_state.chroma_path != "":
    peeker = ChromaPeek(st.session_state.chroma_path)

    ## create radio button of each collection
    col1, col2 = st.columns([1,3])
    with col1:
        collection_selected=st.radio("select collection to view",
                 options=peeker.get_collections(),
                 index=0,
                 )
        
    with col2:
        df = peeker.get_collection_data(collection_selected, dataframe=True)

        st.markdown(f"<b>Data in </b>*{collection_selected}*", unsafe_allow_html=True)
        st.dataframe(df, use_container_width=True, height=300)
        
    st.divider()

    query = st.text_input("Enter Query to get 3 similar texts", placeholder="get 3 similar texts")
    if query:
        result_df = peeker.query(query, collection_selected, dataframe=True)
        
        st.dataframe(result_df, use_container_width=True)

else:
    st.subheader("Enter Valid Full Persist Path")
