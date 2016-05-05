#!/bin/sh

echo "Installing Python modules..."
pip install -r requirements.txt
echo "Downloading WordNet synonym database..."
python -m nltk.downloader wordnet
