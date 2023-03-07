FROM docker:dind
RUN apk add curl
RUN apk add py3-pip
RUN apk add git
RUN curl https://bootstrap.pypa.io/pip/3.6/get-pip.py -o get-pip.py && python get-pip.py
COPY requirements.txt .
RUN pip3 install -r requirements.txt

