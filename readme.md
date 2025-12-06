# 📄 Resume Chatbot - AI-Powered Resume Assistant

An intelligent chatbot that answers questions about your resume using RAG (Retrieval Augmented Generation) and LangGraph.

![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-1.28%2B-red)
![LangChain](https://img.shields.io/badge/LangChain-Latest-green)
![Groq](https://img.shields.io/badge/Groq-Free%20API-orange)

## 🌟 Features

- 💬 **Interactive Chat Interface** - Ask questions about resume in natural language
- 🧠 **Smart Context Retrieval** - Uses RAG to find relevant information
- 📚 **Chat History** - Multiple conversation threads with persistence
- ⚡ **Fast Responses** - Powered by Groq's lightning-fast LLMs
- 📤 **PDF Upload** - Easy resume upload through UI
- 💾 **Vector Store Caching** - Fast loading after first setup

## 📋 Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- A Groq API key (free - see setup below)

## 🚀 Quick Start Guide

### 1️⃣ Clone the Repository

```bash
git clone https://github.com/yourusername/resume-chatbot.git
cd resume-chatbot
```

### 2️⃣ Create Virtual Environment (Recommended)

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**Mac/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

### 4️⃣ Get Your Free Groq API Key

1. Go to [https://console.groq.com](https://console.groq.com)
2. Sign up for a free account (takes 30 seconds)
3. Click on "API Keys" in the left sidebar
4. Click "Create API Key"
5. Copy your API key

### 5️⃣ Configure API Key

Open `backend.py` and replace the API key on line 12:

```python
groq_api_key="YOUR_GROQ_API_KEY_HERE",  # Paste your key here
```

**💡 Pro Tip:** For better security, use environment variables:

Create a `.env` file in the project root:
```
GROQ_API_KEY=your_actual_api_key_here
```

Then update `backend.py`:
```python
from dotenv import load_dotenv
load_dotenv()

model = ChatGroq(
    model="llama-3.3-70b-versatile",
    groq_api_key=os.getenv("GROQ_API_KEY"),
    temperature=0.7,
)
```

### 6️⃣ Add Your Resume

Place your resume PDF in the project folder with one of these names:
- `resume.pdf` (recommended)
- `cv.pdf`
- `my_resume.pdf`

### 7️⃣ Run the Application

```bash
streamlit run app.py
```

The app will open automatically in your browser at `http://localhost:8501`

## 📁 Project Structure

```
resume-chatbot/
├── app.py                      # Streamlit frontend
├── backend.py                  # LangGraph chatbot logic
├── requirements.txt            # Python dependencies
├── README.md                   # This file
├── .gitignore                  # Git ignore file
├── resume.pdf                  # Your resume (add this)
└── resume_vectorstore/         # Auto-generated vector database
```

## 📦 Requirements.txt

Create a `requirements.txt` file with:

```
streamlit>=1.28.0
langchain>=0.1.0
langchain-groq>=0.0.1
langchain-community>=0.0.1
langgraph>=0.0.20
faiss-cpu>=1.7.4
pypdf>=3.17.0
sentence-transformers>=2.2.2
python-dotenv>=1.0.0
```

## 🔧 Configuration Options

### Change the LLM Model

In `backend.py`, you can change the model:

```python
model = ChatGroq(
    model="llama-3.3-70b-versatile",  # Options below
    # Other options:
    # "mixtral-8x7b-32768" - Good for longer contexts
    # "llama-3.1-70b-versatile" - Alternative Llama model
    # "gemma2-9b-it" - Smaller, faster model
)
```

### Adjust Retrieval Settings

In `backend.py`, modify retrieval parameters:

```python
retriever = vectorstore.as_retriever(
    search_type="similarity",
    search_kwargs={"k": 3}  # Number of chunks to retrieve (1-10)
)
```

### Change Chunk Sizes

In `backend.py`, adjust text splitting:

```python
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,      # Size of each chunk (500-2000)
    chunk_overlap=200,    # Overlap between chunks (100-400)
)
```

## 💡 Usage Examples

Once running, try asking:

**About Experience:**
- "What companies have I worked for?"
- "Tell me about my last role"
- "What were my responsibilities at [Company]?"

**About Skills:**
- "What programming languages do I know?"
- "List my technical skills"
- "What frameworks have I used?"

**About Education:**
- "Where did I study?"
- "What degree do I have?"
- "What's my educational background?"

**About Projects:**
- "Tell me about my projects"
- "What technologies did I use in [Project]?"
- "Describe my achievements"

## 🐛 Troubleshooting

### Issue: "ImportError: cannot import name 'ChatGroq'"

**Solution:**
```bash
pip install --upgrade langchain-groq
```

### Issue: "No module named 'sentence_transformers'"

**Solution:**
```bash
pip install sentence-transformers
```

### Issue: "Resume not loaded"

**Solutions:**
1. Make sure your PDF is named `resume.pdf`, `cv.pdf`, or `my_resume.pdf`
2. Place it in the same folder as `app.py`
3. Restart the application
4. Or upload through the "Upload Resume" section in the sidebar

### Issue: "Groq API quota exceeded"

**Solutions:**
- Free tier has generous limits (30 req/min, 14.4K/day)
- Wait a minute and try again
- Check your usage at https://console.groq.com

### Issue: "Vector store error"

**Solution:**
```bash
# Delete the vector store folder and restart
rm -rf resume_vectorstore/  # Mac/Linux
rmdir /s resume_vectorstore  # Windows
```

## 🔒 Security Best Practices

1. **Never commit API keys to Git**
   ```bash
   # Add to .gitignore
   .env
   *.key
   ```

2. **Use environment variables**
   ```python
   import os
   from dotenv import load_dotenv
   load_dotenv()
   api_key = os.getenv("GROQ_API_KEY")
   ```

3. **Keep dependencies updated**
   ```bash
   pip install --upgrade -r requirements.txt
   ```

## 🎨 Customization

### Change Colors/Theme

Edit the CSS in `app.py`:

```python
st.markdown("""
    <style>
    .stApp header {
        background-color: #your-color;  # Change header color
    }
    </style>
""", unsafe_allow_html=True)
```

### Add More Features

- **Export conversations:** Add export to PDF/TXT functionality
- **Multi-language:** Add translation support
- **Voice input:** Integrate speech-to-text
- **Analytics:** Track popular questions

## 📊 Performance Tips

1. **Smaller PDFs load faster** - Keep resume under 5 pages
2. **Reduce chunk size** for faster retrieval
3. **Cache vector store** (done automatically)
4. **Use smaller models** for faster responses (e.g., `gemma2-9b-it`)

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [LangChain](https://langchain.com/) - For the amazing framework
- [Groq](https://groq.com/) - For free, fast LLM API
- [Streamlit](https://streamlit.io/) - For the beautiful UI framework
- [Hugging Face](https://huggingface.co/) - For sentence transformers

## 📧 Contact

For questions or suggestions, please open an issue on GitHub.

## 🔗 Useful Links

- [Groq Documentation](https://console.groq.com/docs)
- [LangChain Documentation](https://python.langchain.com/)
- [Streamlit Documentation](https://docs.streamlit.io/)
- [LangGraph Tutorial](https://langchain-ai.github.io/langgraph/)

---

Made with ❤️ using LangGraph and Streamlit