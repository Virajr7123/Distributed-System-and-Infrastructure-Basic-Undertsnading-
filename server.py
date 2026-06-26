import socket
import json
import threading
import traceback
from storage import StorageEngine
HOST = "127.0.0.1"
PORT = 9099
class DatabaseServer:
    def __init__(self, host=HOST, port=PORT):
        self.host = host
        self.port = port
        self.db = StorageEngine()
        self.is_running = False
    def start(self):
        self.is_running = True
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.settimeout(1.0)
        try:
            server_socket.bind((self.host, self.port))
            server_socket.listen(5)
            print(f"[Server] Database server is listening on {self.host}:{self.port}...")
            while self.is_running:
                try:
                    client_sock, client_addr = server_socket.accept()
                    print(f"[Server] New connection established from {client_addr[0]}:{client_addr[1]}")
                    client_handler = threading.Thread(
                        target=self.handle_client,
                        args=(client_sock, client_addr),
                        daemon=True
                    )
                    client_handler.start()
                except socket.timeout:
                    continue
        except KeyboardInterrupt:
            print("[Server] Shutting down database server...")
        except Exception as e:
            print(f"[Server Error] {e}")
        finally:
            server_socket.close()
            self.is_running = False
    def handle_client(self, client_sock, client_addr):
        client_file = client_sock.makefile('r', encoding='utf-8')
        try:
            for line in client_file:
                line = line.strip()
                if not line:
                    continue
                try:
                    request = json.loads(line)
                    response = self.process_request(request)
                except json.JSONDecodeError:
                    response = {
                        "status": "error",
                        "message": "Invalid JSON format. Commands must be valid line-delimited JSON objects."
                    }
                except Exception as e:
                    response = {
                        "status": "error",
                        "message": f"Server error: {str(e)}"
                    }
                response_str = json.dumps(response) + "\n"
                client_sock.sendall(response_str.encode('utf-8'))
        except ConnectionResetError:
            print(f"[Server] Connection reset by client {client_addr[0]}:{client_addr[1]}")
        except Exception as e:
            print(f"[Server Error] Handling client {client_addr[0]}:{client_addr[1]} failed: {e}")
            traceback.print_exc()
        finally:
            client_file.close()
            client_sock.close()
            print(f"[Server] Connection closed with client {client_addr[0]}:{client_addr[1]}")
    def process_request(self, request):
        action = request.get("action", "").upper()
        if action == "SET":
            key = request.get("key")
            value = request.get("value")
            if key is None or value is None:
                return {"status": "error", "message": "Missing 'key' or 'value' parameters for SET action."}
            self.db.set(key, value)
            return {"status": "success"}
        elif action == "GET":
            key = request.get("key")
            if key is None:
                return {"status": "error", "message": "Missing 'key' parameter for GET action."}
            value = self.db.get(key)
            if value is None:
                return {"status": "error", "message": "Key not found."}
            return {"status": "success", "value": value}
        elif action == "DELETE":
            key = request.get("key")
            if key is None:
                return {"status": "error", "message": "Missing 'key' parameter for DELETE action."}
            deleted = self.db.delete(key)
            if not deleted:
                return {"status": "error", "message": "Key not found."}
            return {"status": "success"}
        elif action == "KEYS":
            keys = self.db.list_keys()
            return {"status": "success", "keys": keys}
        else:
            return {"status": "error", "message": f"Unknown action: '{action}'."}
if __name__ == "__main__":
    server = DatabaseServer()
    server.start()
