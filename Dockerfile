FROM python:3.10-slim-bullseye

ENV PYTHONUNBUFFERED=1
ENV PYTHONIOENCODING=UTF-8
#ENV HOST=0.0.0.0
#ENV LISTEN_PORT 8080
 
EXPOSE 8501
 
 
COPY ./requirements.txt /app/requirements.txt
 
RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt
 
WORKDIR app/
 
COPY ./sop_bot /app/sop_bot
COPY ./.streamlit /app/.streamlit

 
CMD ["streamlit", "run", "sop_bot/main.py", "--server.port", "8501", "--server.address=0.0.0.0"]