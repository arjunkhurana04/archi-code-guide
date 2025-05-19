## ArchiCode Guide 🏗️🤖

A modern AI-powered architectural code assistant
ArchiCode Guide transforms how architects, engineers, and builders navigate complex building codes. This intelligent assistant instantly retrieves, interprets, and explains architectural regulations, letting you focus on design rather than drowning in documentation.

✨ Features
• Instant Code Lookup: Get immediate answers to any building code question • Natural Language Interface: Ask questions in plain English, no complex query syntax needed • Context-Aware Responses: The assistant understands the context of your project and provides relevant information • Fire & Life Safety Only: Currently works only for NBC fire and life safety regulations • Interactive Chat Experience: Powered by Chainlit for a smooth, chat-based interface • Multi-modal Support: Upload relevant diagrams or plans for context-specific guidance • Citation Support: All responses include references to specific code sections

🚀 Getting Started
Prerequisites: • Python 3.8+ • Git
Installation:
1.	Clone the repository 
2.	Create a virtual environment python -m venv venv source venv/bin/activate # On Windows: venv\Scripts\activate
3.	Install dependencies pip install -r requirements.txt
Environment Setup: Create a .env file in the root directory and add your API keys: OPENAI_API_KEY=your_openai_api_key

💻 Usage
Start the Chainlit app: chainlit run main.py
Then open your browser and navigate to http://localhost:8000
Example Questions: "What are the requirements for fire separations in residential buildings?", "Explain the exit requirements for a 3-story office building", "Show me the fire resistance ratings for load-bearing walls" 

🔧 How It Works
1.	Data Preparation: Building codes are extracted, chunked, and stored using extract_and_chunk.py
2.	Vector Storage: Processed data is saved in a pickle file (nbc_fire_and_life_safety.pkl)
3.	Query Processing: When you ask a question, the system:
o	Analyzes your query
o	Retrieves relevant code sections
o	Generates a comprehensive response with citations
o	Presents the answer through a conversational interface

🛠️ Technologies
• Chainlit: Powerful framework for building LLM-powered chat applications • OpenAI API: Powers the natural language understanding • LangChain: Framework for developing applications powered by language models • Python: Core programming language

Built with ❤️ for architects and builders everywhere
