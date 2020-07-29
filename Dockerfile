from fnndsc/ubuntu-python3:latest

RUN apt-get update \
    && apt-get install -y \
        vim \
        curl \
    && rm -rf /var/lib/apt/lists/*

RUN /usr/bin/python3 -m pip install --upgrade pip

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD [ "./metrics.py" ]
