conda create -n manufacturing-ai python=3.11 -y

conda activate manufacturing-ai

pip install -r requirements.txt

copy .env.example .env

python scripts\generate_data.py

python scripts\init_database.py

python scripts\build_knowledge_index.py

streamlit run frontend\Home.py