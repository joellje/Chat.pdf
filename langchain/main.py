from flask import Flask, request, jsonify, make_response
from flask_cors import CORS
from PyPDF2 import PdfReader
from langchain_community.vectorstores import FAISS
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
import os
from langchain.chains.question_answering import load_qa_chain
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

def getFilePath(chat_id):
    filename = f"Chat_{chat_id}.pdf"
    file_path = os.path.join('uploads', filename)
    return file_path

def getFileName(chat_id):
    return chat_id_to_filename_map.get(chat_id, "")

def initChain(file_path):
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
        chain = load_qa_chain(OpenAI(), chain_type="stuff")

        return docsearch, chain

    except Exception as e:
        raise Exception(f"Error initializing chain: {e}")
    
def get_output(file_path, query, chat_id):
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
        prompt = hub.pull("rlm/rag-prompt")
        llm = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0)

        rag_chain = (
            {"context": retriever , "question": RunnablePassthrough()}
            | prompt
            | llm
            | StrOutputParser()
        )

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

        return make_response(jsonify({"message": "File uploaded"}), 200)
    
    except Exception as e:
        return make_response(jsonify({"error": str(e)}), 500)

@app.route('/query', methods=['POST'])
def query():
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

        file_path = getFilePath(chat_id)
        output_text = get_output(file_path, query, chat_id)

        return make_response(jsonify({"output": output_text}), 200)
    
    except KeyError:
        return make_response(jsonify({"error": "No query provided"}), 400)
    
    except Exception as e:
        return make_response(jsonify({"error": str(e)}), 500)
    
@app.route('/chats', methods=['GET'])
def get_chats():
    try:
        return make_response(jsonify({"chats": chat_id_to_filename_map}), 200)
    
    except Exception as e:
        return make_response(jsonify({"error": str(e)}), 500)

if __name__ == '__main__':
    app.run(debug=True, host='localhost', port=8080)