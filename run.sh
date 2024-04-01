# Check if the ServerDirectory directory exists
cd langchain

if [ -d "uploads" ]; then
    rm -r uploads
fi

mkdir uploads

python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
playwright install

# Run the main Python script
python main.py