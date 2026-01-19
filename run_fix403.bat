@echo off
if not exist database mkdir database
if not exist data mkdir data
streamlit run app.py --server.port 8502 --server.enableCORS false --server.enableXsrfProtection false
