from flask import Flask, request, jsonify, make_response, g
from flask_cors import CORS
from PyPDF2 import PdfReader
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
import os
from langchain.chains.question_answering import load_qa_chain
from langchain_openai import OpenAI

from dotenv import load_dotenv
load_dotenv()
OPENAI_API_KEY= os.getenv("OPENAI_API_KEY")

app = Flask(__name__)
CORS(app)

docsearch = None
chain = None

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

@app.route('/upload', methods=['POST'])
def upload():
    global docsearch, chain

    try:
        if 'file' not in request.files:
            return make_response(jsonify({"error": "No file part"}), 400)
        
        file = request.files['file']

        if file.filename == '':
            return make_response(jsonify({"error": "No selected file"}), 400)

        filename = 'file.pdf'
        file_path = os.path.join('uploads', filename)
        file.save(file_path)
        docsearch, chain = initChain(file_path)

        return make_response(jsonify({"message": "File uploaded"}), 200)
    
    except Exception as e:
        return make_response(jsonify({"error": str(e)}), 500)

@app.route('/query', methods=['POST'])
def query():
    try:
        data = request.get_json()
        query = data['query']

        docs = docsearch.similarity_search(query)
        output = chain.invoke({"input_documents": docs, "question": query})
        output_text = output['output_text']
        return make_response(jsonify({"output": output_text}), 200)
    
    except KeyError:
        return make_response(jsonify({"error": "No query provided"}), 400)
    
    except Exception as e:
        return make_response(jsonify({"error": str(e)}), 500)

if __name__ == '__main__':
    app.run(debug=True, host='localhost', port=8080)