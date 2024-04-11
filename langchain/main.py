from flask import Flask, request, jsonify, make_response
from flask_cors import CORS
from PyPDF2 import PdfReader
from langchain_community.vectorstores import FAISS
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
import os
import bs4
from langchain_community.document_loaders import AsyncChromiumLoader
from langchain_community.document_transformers import BeautifulSoupTransformer
from langchain_openai import OpenAI
from langchain.chains import create_history_aware_retriever
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain import hub
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_core.messages import HumanMessage
import collections

from dotenv import load_dotenv
load_dotenv()
OPENAI_API_KEY= os.getenv("OPENAI_API_KEY")

app = Flask(__name__)
CORS(app)

chat_histories = {}
chat_id_to_filename_map = {}
chat_id_to_url_map = {}

def getFilePath(chat_id):
    filename = f"Chat_{chat_id}.pdf"
    file_path = os.path.join('uploads', filename)
    return file_path

def getURL(chat_id):
    return chat_id_to_url_map.get(chat_id, "")

def getChatHistory(chat_id):
    chat_history = chat_histories.get(chat_id, [])
    res = []

    for item in chat_history:
        if isinstance(item, HumanMessage):
            res.append({"isUserSent": True, "message": item.content})
        else:
            res.append({"isUserSent": False, "message": item})

    return res[1:]
    
def get_pdf_output(file_path, query, chat_id):
    try:
        pdf_reader = PdfReader(file_path)
        text = ''
        for page in pdf_reader.pages:
            text += page.extract_text()

        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=512,
            chunk_overlap=32,
            length_function=len,
        )

        texts = text_splitter.split_text(text)
        embeddings = OpenAIEmbeddings()
        docsearch = FAISS.from_texts(texts, embeddings)

        # Retrieve and generate using the relevant snippets of the pdf.
        retriever = docsearch.as_retriever()
        llm = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0)

        contextualize_q_system_prompt = """Given a chat history and the latest user question \
        which might reference context in the chat history, formulate a standalone question \
        which can be understood without the chat history. Do NOT answer the question, \
        just reformulate it if needed and otherwise return it as is."""

        contextualize_q_prompt = ChatPromptTemplate.from_messages(
            [
                ("system", contextualize_q_system_prompt),
                MessagesPlaceholder("chat_history"),
                ("human", "{input}"),
            ]
        )

        history_aware_retriever = create_history_aware_retriever(
            llm, retriever, contextualize_q_prompt
        )

        qa_system_prompt = """You are an assistant for question-answering tasks. \
        Use the following pieces of retrieved context to answer the question. \
        If you don't know the answer, just say that you don't know. \
        Use three sentences maximum and keep the answer concise.\

        {context}"""

        qa_prompt = ChatPromptTemplate.from_messages(
            [
                ("system", qa_system_prompt),
                MessagesPlaceholder("chat_history"),
                ("human", "{input}"),
            ]
        )

        question_answer_chain = create_stuff_documents_chain(llm, qa_prompt)

        rag_chain = create_retrieval_chain(history_aware_retriever, question_answer_chain)

        chat_history = chat_histories[chat_id]
        print("Chat History: ", chat_history)
        
        reply = rag_chain.invoke({"input": query, "chat_history": chat_history})
        res = reply["answer"]
        chat_history.extend([HumanMessage(content=query), res])
    
        return res
    
    except Exception as e:
        raise Exception(f"Error getting output: {e}")
    

def get_url_output(url, query, chat_id):
    try:
        bs_transformer = BeautifulSoupTransformer()
        loader = AsyncChromiumLoader([url])
        html = loader.load()
        webpage = bs_transformer.transform_documents(
            html, tags_to_extract=["p", "li", "div", "a", "section", "ul"])
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200
        )
        docs = text_splitter.split_documents(webpage)

        embeddings = OpenAIEmbeddings()
        docsearch = FAISS.from_documents(docs, embeddings)

        # Retrieve and generate using the relevant snippets of the pdf.
        retriever = docsearch.as_retriever()
        llm = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0)

        contextualize_q_system_prompt = """Given a chat history and the latest user question \
        which might reference context in the chat history, formulate a standalone question \
        which can be understood without the chat history. Do NOT answer the question, \
        just reformulate it if needed and otherwise return it as is."""

        contextualize_q_prompt = ChatPromptTemplate.from_messages(
            [
                ("system", contextualize_q_system_prompt),
                MessagesPlaceholder("chat_history"),
                ("human", "{input}"),
            ]
        )

        history_aware_retriever = create_history_aware_retriever(
            llm, retriever, contextualize_q_prompt
        )

        qa_system_prompt = """You are an assistant for question-answering tasks. \
        Use the following pieces of retrieved context to answer the question. \
        If you don't know the answer, just say that you don't know. \
        Use three sentences maximum and keep the answer concise.\

        {context}"""

        qa_prompt = ChatPromptTemplate.from_messages(
            [
                ("system", qa_system_prompt),
                MessagesPlaceholder("chat_history"),
                ("human", "{input}"),
            ]
        )

        question_answer_chain = create_stuff_documents_chain(llm, qa_prompt)

        rag_chain = create_retrieval_chain(history_aware_retriever, question_answer_chain)

        chat_history = chat_histories[chat_id]
        print("Chat History: ", chat_history)
        
        reply = rag_chain.invoke({"input": query, "chat_history": chat_history})
        res = reply["answer"]
        chat_history.extend([HumanMessage(content=query), res])
    
        return res

    except Exception as e:
        raise Exception(f"Error getting output: {e}")

@app.route('/upload', methods=['POST'])
def upload():
    try:
        # Get the value of a field named 'text' from the form data
        if not request.form["chat_id"]:
            return make_response(jsonify({"error": "No chat_id provided"}), 400)
        
        chat_id = request.form["chat_id"]
        if chat_id not in chat_histories:
            chat_histories[chat_id] = []

        if 'file' not in request.files:
            return make_response(jsonify({"error": "No file part"}), 400)
        
        file = request.files['file']
        chat_id_to_filename_map[chat_id] = file.filename

        if file.filename == '':
            return make_response(jsonify({"error": "No selected file"}), 400)

        file_path = getFilePath(chat_id)
        file.save(file_path)

        return make_response(jsonify({"chatId": chat_id, "chatName": file.filename}), 200)
    
    except Exception as e:
        return make_response(jsonify({"error": str(e)}), 500)
    
@app.route('/url', methods=['POST'])
def url():
    try:
        # Get the value of a field named 'text' from the form data
        if not request.form["chat_id"]:
            return make_response(jsonify({"error": "No chat_id provided"}), 400)
        
        chat_id = request.form["chat_id"]
        if chat_id not in chat_histories:
            chat_histories[chat_id] = []

        if 'url' not in request.form:
            return make_response(jsonify({"error": "No url provided"}), 400)

        url_link = request.form["url"]
        chat_id_to_url_map[chat_id] = url_link

        return make_response(jsonify({"chatId": chat_id, "url": url_link}), 200)
    except Exception as e:
        return make_response(jsonify({"error": str(e)}), 500)

@app.route('/query', methods=['POST'])
def query_pdf():
    try:
        data = request.get_json()
        if not data:
            return make_response(jsonify({"error": "No data provided"}), 400)
        
        if not data['query']:
            return make_response(jsonify({"error": "No query provided"}), 400)
        
        query = data['query']

        if not data['chat_id']:
            return make_response(jsonify({"error": "No chat_id provided"}), 400)
        
        chat_id = data['chat_id']

        if chat_id in chat_id_to_filename_map:
            file_path = getFilePath(chat_id)
            output_text = get_pdf_output(file_path, query, chat_id)
        elif chat_id in chat_id_to_url_map:
            url = getURL(chat_id)
            output_text = get_url_output(url, query, chat_id)
        else:
            return make_response(jsonify({"error": "Chat_id provided is not recognized"}), 400)

        return make_response(jsonify({"output": output_text}), 200)
    
    except KeyError:
        return make_response(jsonify({"error": "No query provided"}), 400)
    
    except Exception as e:
        return make_response(jsonify({"error": str(e)}), 500)
    
@app.route('/chats', methods=['GET'])
def get_chats():
    try:
        response = []
        for chat_id, filename in chat_id_to_filename_map.items():
            response.append({"chatId": chat_id, "chatName": filename})
        for chat_id, url in chat_id_to_url_map.items():
            response.append({"chatId": chat_id, "chatName": url})
        return make_response(jsonify({"chats": response}), 200)
    
    except Exception as e:
        return make_response(jsonify({"error": str(e)}), 500)

# Get the value of a field named 'chat_id' from the query parameters
@app.route('/chatHistory', methods=['GET'])
def get_chat_histories():
    try:
        chat_id = request.args.get('chat_id')
        chat_history = getChatHistory(chat_id)

        return make_response(jsonify({"chat_history": chat_history}), 200)
    
    except Exception as e:
        return make_response(jsonify({"error": str(e)}), 500)

if __name__ == '__main__':
    app.run(debug=True, host='localhost', port=8080)