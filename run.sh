# Check if the ServerDirectory directory exists
cd langchain

if [ ! -d "uploads" ]; then
    mkdir uploads
fi

python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# Run the main Python script
python main.py