# 🎓 NextLeap AI Advisor

An intelligent RAG (Retrieval-Augmented Generation) chatbot designed to provide accurate, grounded information about NextLeap fellowship programs.

![Deploy to Vercel](https://vercel.com/button)

## 🌟 Features

- **Grounded Responses**: Powered by Groq/OpenAI and ChromaDB, ensuring no hallucinations.
- **Detailed Curriculum**: Contains scraped syllabi for PM, UX, Data Analyst, Business Analyst, and GenAI courses.
- **Unified Deployment**: Next.js frontend and Python FastAPI backend hosted seamlessly on Vercel.
- **Daily Sync**: Automated GitHub Actions to scrape latest course data and update the knowledge base.
- **Standalone Option**: Includes a Streamlit version for quick demos.

## 🏗️ Technical Stack

- **Frontend**: Next.js 14 (TailwindCSS, Framer Motion, Lucide)
- **Backend API**: FastAPI (Python 3.9+)
- **Vector Database**: ChromaDB
- **LLM Engine**: Groq (Llama 3 70B) or OpenAI
- **Embeddings**: Sentence-Transformers / OpenAI text-embedding-3-small
- **Scheduler**: GitHub Actions + Python Scrapers

## 🚀 Getting Started

### Prerequisites
- Python 3.9+
- Node.js 18+
- API Keys: [Groq Cloud](https://console.groq.com/) and [OpenAI](https://platform.openai.com/)

### Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/manishkumar98/nextleap-courseinfo-rag-chatbot.git
   cd nextleap-courseinfo-rag-chatbot
   ```

2. **Setup Backend**:
   ```bash
   pip install -r requirements.txt
   cp .env.example .env # Add your keys here
   ```

3. **Setup Frontend**:
   ```bash
   npm install
   ```

4. **Run Locally**:
   - Backend: `python main.py`
   - Frontend: `npm run dev`

## 📊 Project Structure

- `app/`: Next.js frontend application.
- `api/`: Vercel serverless functions (FastAPI).
- `src/`: Core RAG logic (retrieval, generation, chunking).
- `data/`: Vector database and synchronization status.
- `.github/workflows/`: Automated daily sync configuration.

## 🚢 Deployment

### Vercel (Unified App)
1. Project Root Directory: **Leave Empty**.
2. Framework Preset: **Next.js**.
3. Add Environment Variables: `OPENAI_API_KEY`, `GROQ_API_KEY`.

### Streamlit (Standalone)
Link your repo to [Streamlit Cloud](https://share.streamlit.io) and set the main file to `streamlit_app.py`.

## 📜 License
MIT
