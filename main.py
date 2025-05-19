import sys
import os
import pickle

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain.chains import (ConversationalRetrievalChain,)
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain.prompts import SystemMessagePromptTemplate, HumanMessagePromptTemplate, ChatPromptTemplate

from langchain_community.chat_message_histories import ChatMessageHistory
from langchain.memory import ConversationBufferMemory
from dotenv import load_dotenv

import chainlit as cl

load_dotenv()

text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)

# Define the system prompt for the assistant
SYSTEM_PROMPT = """You are ArchiCode Guide, an AI assistant built for architects, engineers, and builders
to help them navigate the Indian National Building Code (NBC) 2016, specifically the Fire and Life Safety chapter.

Always provide accurate information from the accessible data given to you with specific citations.
If you're not certain about information, acknowledge the limitations.
When answering questions, follow these guidelines:
1. Provide clear, concise explanations of building code requirements
2. Include specific section numbers and citations when referencing the NBC
3. Explain technical terms in simpler language when appropriate
4. If a question is outside the scope of NBC regulations, clarify this in your response
5. NEVER fabricate answers or interpretations beyond the provided context
6. Only use the provided context to answer questions

You have particular expertise in fire and life safety regulations but can assist with all aspects of the NBC. 
When providing sources, reference them clearly so users can verify the information.
"""


@cl.on_chat_start
async def on_chat_start():

    msg = cl.Message(content=f"**Welcome to ArchiCodeGuide!** \n" f"I'm your personal assistant to help you navigate the NBC standards, regulations, and best practices for construction, safety, and urban development in India. How can I assist you today?")
    await msg.send()

    pickle_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'nbc_fire_and_life_safety.pkl')

    # Add error handling
    try:
        with open(pickle_path, 'rb') as file:
            nbc_data = pickle.load(file)
    except Exception as e:
        # Display error to user
        await cl.Message(content=f"Error loading data: {str(e)}").send()
        return

    texts = nbc_data["chunks"]
    metadatas = [{"source": f"{i}"} for i in nbc_data["metadatas"]]

    # Create a Chroma vector store
    embeddings = OpenAIEmbeddings(model = "text-embedding-3-small")
    docsearch = await cl.make_async(Chroma.from_texts)(
        texts, embeddings, metadatas=metadatas
    )

    message_history = ChatMessageHistory()

    memory = ConversationBufferMemory(
        memory_key="chat_history",
        output_key="answer",
        chat_memory=message_history,
        return_messages=True,
    )

    # Create a custom prompt template with system message
    prompt = ChatPromptTemplate.from_messages([
        SystemMessagePromptTemplate.from_template(SYSTEM_PROMPT),
        HumanMessagePromptTemplate.from_template(
            "Answer the following question about the NBC based on the context provided.\n\n"
            "Question: {question}\n\n"
            "Context: {context}"
        )
    ])

    # Create the model with system prompt support
    llm = ChatOpenAI(model_name="gpt-4o", temperature=0, streaming=True)

    # Create a chain that uses the Chroma vector store with system prompt
    chain = ConversationalRetrievalChain.from_llm(
        llm=llm,
        chain_type="stuff",
        retriever=docsearch.as_retriever(),
        memory=memory,
        return_source_documents=True,
        combine_docs_chain_kwargs={"prompt": prompt}  # Use our custom prompt with system instructions
    )

    # Store the chain and system prompt in the user session
    cl.user_session.set("chain", chain)
    cl.user_session.set("system_prompt", SYSTEM_PROMPT)


@cl.on_message
async def main(message: cl.Message):
    chain = cl.user_session.get("chain")  # type: ConversationalRetrievalChain
    cb = cl.AsyncLangchainCallbackHandler()

    res = await chain.acall(message.content, callbacks=[cb])
    answer = res["answer"]
    source_documents = res["source_documents"]  # type: List[Document]

    text_elements = []  # type: List[cl.Text]

    if source_documents:
        for source_idx, source_doc in enumerate(source_documents):
            source_name = f"source_{source_idx}"
            # Create the text element referenced in the message
            text_elements.append(
                cl.Text(
                    content=source_doc.page_content, name=source_name, display="side"
                )
            )
        source_names = [text_el.name for text_el in text_elements]

        if source_names:
            answer += f"\nSources: {', '.join(source_names)}"
        else:
            answer += "\nNo sources found"

    await cl.Message(content=answer, elements=text_elements).send()


if __name__ == "__main__":
    from chainlit.cli import run_chainlit
    run_chainlit(__file__)