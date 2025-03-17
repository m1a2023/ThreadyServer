# Setting Up ThreadyServer Development Environment

This guide will walk you through installing dependencies, setting up the environment, and running the ThreadyServer project.

---

## Install Dependencies

### Ollama

Download and install Ollama: [Download Ollama](https://ollama.com/)

#### PostgreSQL

Download and install PostgreSQL: [Download PostgreSQL](https://www.postgresql.org/download/)

### Python Dependencies

Install the required Python packages using pip:

```sh
pip install fastapi uvicorn sqlmodel typing httpx dotenv
```

---

## Setting Up the Environment

### Ollama

Install the necessary local model and start the Ollama server.

### PostgreSQL Configuration

1. Set up PostgreSQL, create a database, and connect to it.
2. In the root directory of the project, create a `.env` file and add the following:

```ini
POSTGRES_SERVER=localhost   # Database host
POSTGRES_PORT=5432          # Default PostgreSQL port
POSTGRES_DB=thready         # Database name
POSTGRES_USER=postgres      # Database user
POSTGRES_PASSWORD=postgres  # Database password
```

---

## Starting the Server

Navigate to your project directory and start the server:

```sh
cd <YOUR_PROJECT_NAME>
python src/main.py
```

The ThreadyServer should now be up and running!

---

## Using API Examples:

Use Insomnia, Postman for better experience or use Browser, CURL.

- GET http://localhost:9000/api/db/users/

Sending GET request, returns JSON response of all users contains in DB
