# LangChain-Chatbot
A chatbot for aiding in clinical SOPs


How to run in local
Add your open AI apikey to utils.py ( will update to aws ssm later)
```sh
pip install -r requirements.txt
streamlit run sop_bot/main.py
```

Using docker
```sh
docker build -t langchain-chat-bot .
docker run -p 8501:8501 langchain-chat-bot
```