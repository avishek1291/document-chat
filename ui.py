import sys
from llm_ref import Model
from transcript import DocumentLoader
from splitter import Splitter, Vectors
from config import DOCUMENT_MODE

# Check if running under Streamlit
STREAMLIT_MODE = True
try:
    import streamlit as st
except ImportError:
    STREAMLIT_MODE = False


def render_header():
    """Render the header section."""
    if STREAMLIT_MODE:
        st.title("📄 Document Chat with LLM")
    else:
        print("\n" + "="*50)
        print("📄 Document Chat with LLM")
        print("="*50)


def render_upload_section():
    """Render the document upload section."""
    if STREAMLIT_MODE:
        st.subheader("📤 Upload Your Document")
        
        # Show document mode
        if DOCUMENT_MODE == 'merge':
            st.success(f"🔀 Mode: MERGE - New documents will be added to existing ones")
        else:
            st.warning(f"🔄 Mode: REPLACE - New documents will overwrite previous ones")
        
        st.write("Supported formats: PDF, TXT, DOCX")
        
        # Show already embedded documents
        vectors = Vectors()
        embedded_docs = vectors.get_embedded_documents()
        if embedded_docs:
            st.info(f"📚 Embedded documents: {', '.join(embedded_docs)}")
        
        uploaded_file = st.file_uploader(
            "Choose a document",
            type=['pdf', 'txt', 'docx'],
            help="Upload a document to create embeddings"
        )
        
        if uploaded_file is not None:
            if st.button("Process Document", type="primary", key="upload_button"):
                with st.spinner("Processing document..."):
                    try:
                        # Read file bytes
                        file_bytes = uploaded_file.read()
                        
                        # Extract text from document
                        doc_loader = DocumentLoader()
                        text = doc_loader.extract_text(file_bytes, uploaded_file.name)
                        
                        if not text.strip():
                            st.error("❌ Failed to extract text from document")
                            return
                        
                        # Check if document already embedded
                        vectors = Vectors()
                        is_embedded, message = vectors.is_document_embedded(text, uploaded_file.name)
                        if is_embedded:
                            st.warning(message)
                            return
                        
                        # Split text into chunks
                        splitter = Splitter()
                        documents = splitter.split_text(text)
                        
                        # Generate embeddings and save to FAISS
                        vectors.create_db_from_documents(documents, uploaded_file.name)
                        
                        st.success("✅ Document processed and embeddings saved!")
                        st.info(f"📊 Created {len(documents)} chunks from the document")
                        st.rerun()
                        
                    except Exception as e:
                        st.error(f"❌ Error processing document: {str(e)}")
        
        st.divider()


def render_input_section():
    """Render the input and processing section."""
    if STREAMLIT_MODE:
        st.subheader("❓ Ask Your Question")
        user_input = st.text_area(
            "Enter your question or prompt:",
            placeholder="e.g., summarize it, what is...",
            height=100
        )
    else:
        print("\nAsk Your Question")
        print("-" * 40)
        user_input = input("Enter your question or prompt: ")
    
    return user_input


def process_query(user_input: str) -> None:
    """Process user query and display result."""
    if not user_input.strip():
        if STREAMLIT_MODE:
            st.warning("⚠️ Please enter a question or prompt")
        else:
            print("⚠️ Please enter a question or prompt")
        return
    
    try:
        if STREAMLIT_MODE:
            with st.spinner("Processing your request..."):
                answer = Model().invoke_llm(user_input)
            st.success("✅ Done!")
            st.subheader("📝 Answer:")
            st.write(answer)
        else:
            print("\n⏳ Processing your request...")
            answer = Model().invoke_llm(user_input)
            print("\n✅ Done!")
            print("\nAnswer:")
            print("-" * 40)
            print(answer)
            print("-" * 40)
    except Exception as e:
        if STREAMLIT_MODE:
            st.error(f"❌ Error: {str(e)}")
        else:
            print(f"❌ Error: {str(e)}")


def render_chat_interface():
    """Main function to render the complete chat interface."""
    render_header()
    
    if STREAMLIT_MODE:
        render_upload_section()
        user_input = render_input_section()
        
        if st.button("Get Answer", type="primary"):
            process_query(user_input)
    else:
        # CLI mode - continuous loop
        while True:
            user_input = render_input_section()
            
            if user_input.lower() in ['exit', 'quit', 'q']:
                print("\n👋 Goodbye!")
                break
            
            process_query(user_input)
            
            print("\n" + "-"*50)
            continue_prompt = input("Continue? (yes/no): ").lower()
            if continue_prompt not in ['yes', 'y', '']:
                print("\n👋 Goodbye!")
                break


