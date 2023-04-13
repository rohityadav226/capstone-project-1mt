FROM python:3.10.9
EXPOSE 8501
WORKDIR /home/app
RUN apt-get update && apt-get install -y \
    build-essential \
    software-properties-common \
    git \
    && rm -rf /var/lib/apt/lists/*
COPY ./app /home/app/
RUN pip3 install -r requirements.txt
ENTRYPOINT ["streamlit", "run", "web_app_script.py", "--server.port=8501", "--server.address=0.0.0.0"]