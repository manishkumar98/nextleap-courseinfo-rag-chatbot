# NextLeap RAG Chatbot: Product Vision

This document outlines the core vision, purpose, and operating philosophy of the NextLeap RAG Chatbot.

---

## 🌟 The Vision
To create a "Digital Academic Advisor" that empowers prospective learners with instant, 100% accurate, and verifiable information about NextLeap’s fellowships. 

Unlike generic AI, this chatbot is **grounded**—it doesn't guess. It acts as a bridge between the vast information on NextLeap's website and the user's specific questions.

---

## 📚 The "Library & Librarian" Analogy
To understand how this system works, imagine a very advanced Library:

1.  **The Books (Knowledge Source)**: These are the actual pages of the NextLeap website (PM Fellowship, UI/UX Design, etc.).
2.  **The Index Cards (Vector Database)**: Instead of a user having to read 10 pages, we create detailed "index cards" for every fact. We store these in a way that the computer can search for "meaning" rather than just keywords.
3.  **The Librarian (The AI)**: This is our intelligent interface (powered by LLMs like GPT-4). It doesn't use its own imagination; instead, it reads the specific "index cards" we give it and summarizes the answer for the user.

---

## 🛠️ The Implementation Journey

### 1. Collecting the "Facts" (Data Acquisition)
We sent automated robots to the NextLeap website to perform "Deep Scraping." This isn't just surface text; it includes clicking through menus and carousels to find the precise details that matter:
*   Exact pricing and upcoming deadlines (e.g., the March 8th price hike).
*   Full instructor lists from companies like Microsoft, Meta, and Google.
*   Specific live class timings and placement requirements.

### 2. Teaching the "Facts" to the AI (Embedding & Indexing)
Computers speak in numbers, not just words. We transform our text facts into "Embeddings"—mathematical representations of meaning. This allows the system to understand that a user asking "When is the next batch?" is looking for the "Next Cohort Start Date."

### 3. The Trustworthy Conversation (Retrieval & Generation)
When a user asks a question, the system:
1.  **Retrieves** the most relevant facts from our index.
2.  **Attaches** the exact website URL to those facts.
3.  **Constructs** an answer that includes a citation, so the user can verify the information themselves.

---

## 🔄 The "Heartbeat" (Automated Sync)
Websites are dynamic. To ensure our chatbot never gives outdated info:
*   **Continuous Learning**: Every 24 hours, the system automatically checks the NextLeap website for updates.
*   **Smart Updates**: If a price changes or a new mentor joins, the system detects the change, updates its "index cards," and the chatbot is immediately smarter.

---

## 🎯 Success Metrics
*   **Accuracy**: Zero hallucinations. If the info isn't on the site, the bot says "I don't know."
*   **Trust**: Every answer must be traceable back to a `nextleap.app` URL.
*   **Experience**: Premium, fast, and helpful responses that mirror the NextLeap brand quality.
