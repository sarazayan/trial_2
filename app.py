import streamlit as st
from langchain.vectorstores import Chroma
from langchain.chains import RetrievalQA
from langchain.llms import GooglePalm
from langchain.embeddings import GooglePalmEmbeddings
from langchain.prompts import PromptTemplate
from langchain.document_loaders import PyPDFLoader
from tempfile import NamedTemporaryFile


# Build prompt
template = """Use the following pieces of context to answer the question at the end. If you don't know the answer, just say that you don't know, don't try to make up an answer. Use three sentences maximum. Keep the answer as concise as possible. Always say "thanks for asking!" at the end of the answer. 
{context}
Question: {question}
Helpful Answer:"""
QA_CHAIN_PROMPT = PromptTemplate.from_template(template)

def generate_response(uploaded_files,google_api_key,query_text):
    # Load document if file is uploaded
    for uploaded_file in uploaded_files:
        if uploaded_file is not None:
            with NamedTemporaryFile(dir='.', suffix='.pdf') as f:
                f.write(uploaded_file.getbuffer())
                loader = PyPDFLoader(f.name)
                pages = loader.load_and_split()
                st.write("Number of pages=  ", len(pages))
                
                # Select embeddings
                embeddings = GooglePalmEmbeddings(google_api_key=google_api_key)
                
                # Create a vectorstore from documents
                db = Chroma.from_documents(pages, embeddings) 
                
                # Create retriever interface
                retriever = db.as_retriever(k=3)
                # retriever = db.as_retriever(k=2, fetch_k=4)
                # retriever = db.as_retriever(search_type="similarity_score_threshold", search_kwargs={"score_threshold": .9})
                
                # Create QA chain
                #qa = RetrievalQA.from_chain_type(llm=GooglePalm(google_api_key=google_api_key, temperature=0.1, max_output_tokens=128), chain_type="stuff", retriever=retriever)
                qa = RetrievalQA.from_chain_type(llm=GooglePalm(google_api_key=google_api_key, temperature=0.1, max_output_tokens=128),
                                                 chain_type="stuff",
                                                 retriever=retriever,
                                                 return_source_documents=True,
                                                 chain_type_kwargs={"prompt": QA_CHAIN_PROMPT})
        
                try:
                  res = qa({"query": query_text})
                  return res  
                except:
                  st.write("An error occurred")
    
            return


# Page title
st.set_page_config(page_title='Ask your PDF via PaLM🌴 Model , LangChain 🦜🔗 and Chroma vector DB. By: Ibrahim Sobh')
st.title('Ask your PDF via PaLM🌴 Model , LangChain 🦜🔗 and Chroma vector DB. By: Ibrahim Sobh')

# File upload
#uploaded_file = st.file_uploader('Upload text file', type='txt')
uploaded_files = st.file_uploader('Upload pdf file', type=['pdf'],accept_multiple_files=True)

# Query text
query_text = st.text_input('Enter your question:', placeholder = 'Please provide a short summary.')

# Form input and query
result = []
with st.form('myform', clear_on_submit=True):
    google_api_key = st.text_input('Google PaLM🌴 API Key', type='password')
    submitted = st.form_submit_button('Submit')
    if submitted and google_api_key:
        with st.spinner('Calculating...'):
            response = generate_response(uploaded_files, google_api_key, query_text)
            if response:
                result.append(response)
            del google_api_key

if len(result):
    st.markdown('**Answer:** **:blue[' + response['result'] + "]**")
    st.markdown('---')
    st.markdown('**References:** ')
    for i, sd in enumerate(response['source_documents']):
        st.markdown('**Page:** :green[' + str(sd.metadata["page"]) + "]")

