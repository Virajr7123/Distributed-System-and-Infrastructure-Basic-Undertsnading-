# Distributed System and Infrastructure

A simple, custom key-value database system built with Python. It consists of a database server that handles client connections, stores data, and persists it to a JSON snapshot file, along with a command-line interface (CLI) client for interacting with the database.

## Files

- `server.py`: The main server script that listens for client connections and processes database operations.
- `client.py`: The CLI client used to connect to the server and send commands.
- `storage.py`: The storage engine that handles data persistence in `db_snapshot.json`.
- `db_snapshot.json`: The JSON file where the key-value data is stored and retrieved.

## How to Run

### 1. Start the Server

Before running the client, you need to start the database server. Open a terminal or command prompt and run the following command:

```bash
python server.py
```

You should see an output indicating that the server is listening:
`[Server] Database server is listening on 127.0.0.1:9099...`

### 2. Start the Client

Open a **new** terminal or command prompt window (keep the server running in the other window) and start the client:

```bash
python client.py
```

Once connected, you will see the `db>` prompt where you can start entering commands.

## Available Commands

Once the client is running, you can use the following commands to interact with the database:

- `SET <key> <value>`: Store a key and its value in the database.
- `GET <key>`: Retrieve the value associated with a key.
- `DELETE <key>`: Remove a key from the database.
- `KEYS`: List all keys stored in the database.
- `HELP`: Show the list of available commands.
- `EXIT` or `QUIT`: Disconnect and exit the client.

### Example Usage:

```bash
db> SET my_key "Hello World"
OK
db> GET my_key
Hello World
db> KEYS
Keys: my_key
db> DELETE my_key
OK (Deleted)
```
