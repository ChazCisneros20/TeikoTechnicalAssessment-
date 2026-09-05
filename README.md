... 
setup:
    pip install -r requirements.txt

pipeline: setup
    python load_data.py
    python part2_analysis.py
    python part3_stats.py
    python part4_queries.py

dashboard:
    streamlit run dashboard.py