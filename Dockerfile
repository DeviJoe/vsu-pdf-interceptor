FROM python:3.9

WORKDIR /app
COPY requirements.txt .
RUN pip install --upgrade pip setuptools wheel
RUN pip install pyOpenSSL
RUN pip install python3-ldap
RUN apt-get -y update
RUN apt-get install -y --no-install-recommends ocrmypdf
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY . .

ENTRYPOINT ["python3", "/app/interceptor_bot.py"]

