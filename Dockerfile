from python:slim

RUN apt-get update && apt-get install -y --no-install-recommends \
        varnish \
    && rm -rf /var/lib/apt/lists/*

RUN /usr/local/bin/python -m pip install --upgrade pip

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

USER 9000

CMD ["python", "./metrics.py", "&&", "/usr/sbin/varnishd", "-a", ":8080", "-b", "localhost:8081" ]]
