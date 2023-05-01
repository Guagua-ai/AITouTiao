# GPT News Feeds

This is a server that provides a REST API for the GPT News Feeds. 

The server is built with Python 3.9 and Flask. The server is deployed on a Debian 10.9 server with Nginx and Gunicorn.

## Installation

### Prerequisites

- Python 3.9+
- PostgreSQL 13.2+
- Redis 6.2.3+

```bash
sudo apt-get install python3 python3-pip
```

### Clone the repository

```bash
git clone https://github.com/Michae-zHOU/gpt_news_feed.git
```

### Install the dependencies

```bash
cd gpt_news_feed
pip3 install -r requirements.txt
```

### Run the prod server

```bash
make prod
```

### Run the workflow server

```bash
make workflow
```

## Usage

### Collect the news feed

```bash
curl -X GET http://localhost:8080/collect
```

### Get the news feed

```bash
curl -X GET http://localhost:8080/tweets
```

### Get the news feed with a specific keyword

```bash
curl -X GET http://localhost:8080/chat?keyword=keyword
```

## Documentation

[TBD]

## License

CopyRight © 2022-2023 [Virtual Dynamic Labs, LLC](https://www.virtualdynamiclabs.xyz/)
All Rights Reserved.
