FROM python:3.12-slim

RUN apt-get update \
    && apt-get install -y --no-install-recommends g++ \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY main.cpp /app/main.cpp
COPY server.py /app/server.py
COPY web/ /app/web/

RUN g++ -std=c++17 -O2 -Wall -Wextra /app/main.cpp -o /app/threatlens \
    && chmod +x /app/threatlens

ENV HOST=0.0.0.0
ENV PORT=10000

EXPOSE 10000

CMD ["python", "-u", "server.py"]
