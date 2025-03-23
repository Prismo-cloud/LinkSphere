import streamlit as st
import chromadb
import json

def create_chroma_client(host, port):
    return chromadb.HttpClient(host=host, port=port)

if 'chroma_client' not in st.session_state:
    st.session_state['chroma_client'] = None

st.set_page_config(layout="wide", page_icon="./assets/LinkSphere_Logo.png")

st.image("./assets/LinkSphere_Logo.jpg", width=300)

st.markdown("""
    <style>
        .css-1v3fvcr {display: none;}  
        .css-ffhzg2 {display: none;}   
        .login-container {
            width: 50%;  
            margin: 0 auto;
        }
        .css-1y5j94v {
            width: 100%;
        }
    </style>
""", unsafe_allow_html=True)

if st.session_state['chroma_client'] is None:
    st.header("Database Connection")
    
    with st.container():
        st.markdown('<div class="login-container">', unsafe_allow_html=True)
        
        host = st.text_input("Database Address (Host)", "localhost")
        port = st.number_input("Port", value=8000, min_value=1)
        
        if st.button("Connect"):
            try:
                st.session_state['chroma_client'] = create_chroma_client(host, port)
                st.success(f"Connection successful: {host}:{port}")
                st.session_state['host'] = host
                st.session_state['port'] = port
                st.rerun()  
            except Exception as e:
                st.error(f"Connection error: {e}")
        
        st.markdown('</div>', unsafe_allow_html=True)  

else:
    chroma_client = st.session_state['chroma_client']
    
    st.sidebar.title("Collections")
    
    collections = chroma_client.list_collections()
    collection_names = [collection.name for collection in collections] if collections else []

    selected_collection_name = st.sidebar.radio("Select a Collection", collection_names) if collection_names else None

    if "show_add_collection" not in st.session_state:
        st.session_state["show_add_collection"] = False

    if st.sidebar.button(" Add New Collection"):
        st.session_state["show_add_collection"] = True

    if st.session_state["show_add_collection"]:
        with st.sidebar.form("new_collection_form"):
            new_collection_name = st.text_input("Collection Name")
            submitted = st.form_submit_button(" Create")
            if submitted and new_collection_name:
                chroma_client.get_or_create_collection(name=new_collection_name)
                st.session_state["show_add_collection"] = False  
                st.rerun()  

    st.markdown("---")
    st.subheader("Database Information")

    if selected_collection_name:
        collection = chroma_client.get_or_create_collection(name=selected_collection_name)
        results = collection.get()

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Selected Collection", selected_collection_name)
        col2.metric("Total Data", len(results["ids"]) if "ids" in results else 0)
        col4.metric("Indexes", "1")

        st.markdown("---")
        st.subheader(f" {selected_collection_name} Collection Data")

        if results and "documents" in results and results["documents"]:
            json_data = json.dumps(results, indent=4)
            editable_json = st.text_area("JSON Data", value=json_data, height=300)
            try:
                results = json.loads(editable_json)
            except json.JSONDecodeError:
                st.error("Invalid JSON format!")
        else:
            st.warning(f"No data found in the {selected_collection_name} collection.")

        if st.button(" Delete Collection"):
            chroma_client.delete_collection(name=selected_collection_name)
            st.rerun()  

    else:
        st.info("Please select a collection.")
    
    with st.sidebar:
        if st.button("Logout"):
            st.session_state['chroma_client'] = None
            st.rerun()
