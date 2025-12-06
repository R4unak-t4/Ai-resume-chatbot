from langgraph.graph import START,StateGraph,END,add_messages
from langchain_groq import ChatGroq
from typing import Annotated,TypedDict
from langchain_core.messages import BaseMessage,HumanMessage,SystemMessage
from langgraph.checkpoint.memory import MemorySaver
from langchain_community.document_loaders import PyPDFLoader,DirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
import os

# Initialize Groq model
# Get your free API key from: https://console.groq.com
model=ChatGroq(
    model = "llama-3.3-70b-versatile",
    groq_api_key = "YOUR API KEY",  # Replace with your Groq API key
    temperature = 0.7,
    max_retries = 2,
)

# Initialize embeddings
embeddings=HuggingFaceEmbeddings(
    model_name = "sentence-transformers/all-MiniLM-L6-v2",
    model_kwargs = {'device':'cpu'}
)

# Global variables for vector store
vectorstore=None
retriever=None


def load_and_process_pdfs(pdf_directory: str):
    """Load resume PDFs from a directory and create a vector store"""
    global vectorstore,retriever

    loader=DirectoryLoader(
        pdf_directory,
        glob = "**/*.pdf",
        loader_cls = PyPDFLoader,
        show_progress = True
    )
    documents=loader.load()

    text_splitter=RecursiveCharacterTextSplitter(
        chunk_size = 1000,
        chunk_overlap = 200,
        length_function = len,
        separators = ["\n\n","\n","."," ",""]
    )
    chunks=text_splitter.split_documents(documents)

    vectorstore=FAISS.from_documents(chunks,embeddings)
    retriever=vectorstore.as_retriever(
        search_type = "similarity",
        search_kwargs = {"k":3}
    )

    print(f"✓ Loaded {len(documents)} resume documents")
    print(f"✓ Created {len(chunks)} searchable chunks")
    return vectorstore


def load_single_pdf(pdf_path: str):
    """Load a single resume PDF and add to vector store"""
    global vectorstore,retriever

    loader=PyPDFLoader(pdf_path)
    documents=loader.load()

    text_splitter=RecursiveCharacterTextSplitter(
        chunk_size = 1000,
        chunk_overlap = 200,
        length_function = len
    )
    chunks=text_splitter.split_documents(documents)

    if vectorstore is None:
        vectorstore=FAISS.from_documents(chunks,embeddings)
    else:
        vectorstore.add_documents(chunks)

    retriever=vectorstore.as_retriever(
        search_type = "similarity",
        search_kwargs = {"k":3}
    )

    print(f"✓ Added {len(documents)} documents with {len(chunks)} chunks")
    if vectorstore and hasattr(vectorstore,'index'):
        print(f"✓ Total chunks in database: {vectorstore.index.ntotal}")
    return vectorstore


def save_vectorstore(path: str = "./resume_vectorstore"):
    """Save the vector store to disk"""
    if vectorstore is None:
        print("❌ No vector store to save. Load documents first.")
        return

    vectorstore.save_local(path)
    print(f"✓ Vector store saved to {path}")


def load_vectorstore(path: str = "./resume_vectorstore"):
    """Load a previously saved vector store"""
    global vectorstore,retriever

    try:
        vectorstore=FAISS.load_local(
            path,
            embeddings,
            allow_dangerous_deserialization = True
        )
        retriever=vectorstore.as_retriever(
            search_type = "similarity",
            search_kwargs = {"k":3}
        )
        print(f"✓ Vector store loaded from {path}")
        if vectorstore and hasattr(vectorstore,'index'):
            print(f"✓ Total chunks available: {vectorstore.index.ntotal}")
        return vectorstore
    except Exception as e:
        print(f"❌ Error loading vector store: {e}")
        return None


def is_vectorstore_loaded():
    """Check if vector store is loaded"""
    return vectorstore is not None and retriever is not None


# Resume Assistant System Prompt
RESUME_SYSTEM_PROMPT="""You are a helpful and professional Resume Assistant chatbot. Your role is to help users understand and discuss resume content.

You have access to resume information including:
- Work experience and employment history
- Educational background and qualifications
- Skills (technical, soft skills, languages)
- Projects and achievements
- Certifications and training
- Contact information

Your responsibilities:
1. **Information Retrieval**: Answer questions about specific details in the resume
2. **Experience Discussion**: Explain work history, roles, and responsibilities
3. **Skills Overview**: Highlight technical and soft skills
4. **Project Details**: Describe projects, technologies used, and outcomes
5. **Career Guidance**: Provide insights based on the resume content
6. **Professional Tone**: Maintain a friendly yet professional conversation style

Guidelines:
- Extract specific information from the resume accurately
- Present information in clear, conversational language
- Use bullet points or structured formats when listing multiple items
- If information is not in the resume, politely state that
- Be enthusiastic about achievements and experiences
- Help users understand the candidate's qualifications
- Keep responses concise but informative
- Use a warm, approachable tone

Context from resume:
{context}

Based on the resume content above, provide helpful and accurate responses to questions."""


class ChatMessages(TypedDict):
    messages: Annotated[list[BaseMessage],add_messages]


def retrieve_context(query: str) -> str:
    """Retrieve relevant context from resume"""
    if retriever is None:
        return "⚠️ Resume not loaded."

    try:
        # Use invoke() instead of get_relevant_documents()
        relevant_docs=retriever.invoke(query)
        if not relevant_docs:
            return "⚠️ No relevant information found for this query."

        context="\n\n".join([f"[Section {i + 1}] {doc.page_content}" for i,doc in enumerate(relevant_docs)])
        print(f"Context retrieved: {len(relevant_docs)} chunks")
        return context
    except Exception as e:
        print(f"Error retrieving context: {e}")
        return "⚠️ Error retrieving context."


def chat_node(state: ChatMessages):
    """Process chat with RAG enhancement"""
    messages=state['messages']

    # Get the last user message
    last_message=messages[-1].content if messages else ""

    # Retrieve relevant context
    context=retrieve_context(last_message)

    # Create enhanced prompt with context
    system_message=SystemMessage(
        content = RESUME_SYSTEM_PROMPT.format(context = context)
    )

    # Combine system message with conversation history
    recent_messages=messages[-10:] if len(messages) > 10 else messages
    enhanced_messages=[system_message] + recent_messages

    # Get response from model
    response=model.invoke(enhanced_messages)

    return {'messages':[response]}


# Initialize checkpointer for conversation memory
checkpointer=MemorySaver()

# Build the graph
graph=StateGraph(ChatMessages)
graph.add_node('chat_node',chat_node)
graph.add_edge(START,'chat_node')
graph.add_edge('chat_node',END)

# Compile the chatbot - THIS IS WHAT GETS IMPORTED BY STREAMLIT
chatbot=graph.compile(checkpointer = checkpointer)


def chat(user_input: str,thread_id: str = "default"):
    """Chat with the Resume Assistant (for standalone usage)"""
    config={"configurable":{"thread_id":thread_id}}

    input_messages={
        "messages":[HumanMessage(content = user_input)]
    }

    response=chatbot.invoke(input_messages,config)
    return response['messages'][-1].content