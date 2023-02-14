FROM python:3.7.5
#ARG LOAD_MODELS


WORKDIR /app


# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1


# install dependencies
RUN pip install --upgrade pip
COPY requirements.txt /app/requirements.txt
COPY requirements.txt /app/requirements_AI.txt
RUN --mount=type=cache,target=/root/.cache/pip pip install --no-cache-dir -r requirements.txt --retries 20
RUN if isTrue "$LOAD_MODELS" ; then \
        pip install --no-cache-dir -r requirements_AI.txt --retries 20; \
    fi
RUN python -m spacy download en_core_web_sm
# RUN apt-get install chromium -y


# Now copy in our code, and run it
COPY . /app


RUN if isTrue "$LOAD_MODELS" ; then \
        python -c 'from doc.huggingface_views import *'; \
    fi


# create aliases
RUN echo 'alias pmmm="python manage.py makemigrations"' >> ~/.bashrc
RUN echo 'alias pmm="python manage.py migrate"' >> ~/.bashrc
RUN echo 'alias pmm-fa="python manage.py migrate --database=Fa_DataBase"' >> ~/.bashrc
RUN echo 'alias pmm-en="python manage.py migrate --database=En_DataBase"' >> ~/.bashrc


