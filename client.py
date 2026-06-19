import socket
import json
import sys

HOST = "127.0.0.1"
PORT = 9099

def print_help():
    print("\nAvailable Commands:")
    print("  SET <key> <value>  - Store a key and its value in the database")
    print("  GET <key>          - Retrieve the value associated with a key")
    print("  DELETE <key>       - Remove a key from the database")
    print("  KEYS               - List all keys stored in the database")
    print("  HELP               - Show this list of commands")
    print("  EXIT / QUIT        - Disconnect and exit client")
    print()

def send_request(sock, request_dict):
    try:
        payload = json.dumps(request_dict) + "\n"
        sock.sendall(payload.encode('utf-8'))
        
        response_file = sock.makefile('r', encoding='utf-8')
        response_line = response_file.readline().strip()
        response_file.close()
        
        if not response_line:
            return {"status": "error", "message": "Received empty response from server."}
            
        return json.loads(response_line)
    except Exception as e:
        return {"status": "error", "message": f"Communication failed: {e}"}

def run_client():
    print("==================================================")
    print("           Custom Database CLI Client             ")
    print("==================================================")
    print(f"Connecting to database server at {HOST}:{PORT}...")
    
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((HOST, PORT))
        print("Connected successfully!")
    except ConnectionRefusedError:
        print(f"\n[Error] Could not connect to server at {HOST}:{PORT}.")
        print("Make sure the database server is running (`python server.py`).")
        sys.exit(1)
    except Exception as e:
        print(f"\n[Error] Connection failed: {e}")
        sys.exit(1)
        
    print_help()
    
    try:
        while True:
            try:
                cmd_line = input("db> ").strip()
            except EOFError:
                break
                
            if not cmd_line:
                continue
                
            parts = cmd_line.split(maxsplit=2)
            cmd = parts[0].upper()
            
            if cmd in ("EXIT", "QUIT"):
                print("Disconnecting. Goodbye!")
                break
                
            elif cmd == "HELP":
                print_help()
                continue
                
            elif cmd == "KEYS":
                request = {"action": "KEYS"}
                response = send_request(sock, request)
                if response.get("status") == "success":
                    keys = response.get("keys", [])
                    if keys:
                        print(f"Keys: {', '.join(keys)}")
                    else:
                        print("(empty database)")
                else:
                    print(f"Error: {response.get('message')}")
                    
            elif cmd == "GET":
                if len(parts) < 2:
                    print("Usage: GET <key>")
                    continue
                key = parts[1]
                request = {"action": "GET", "key": key}
                response = send_request(sock, request)
                if response.get("status") == "success":
                    print(response.get("value"))
                else:
                    print(f"Error: {response.get('message')}")
                    
            elif cmd == "DELETE":
                if len(parts) < 2:
                    print("Usage: DELETE <key>")
                    continue
                key = parts[1]
                request = {"action": "DELETE", "key": key}
                response = send_request(sock, request)
                if response.get("status") == "success":
                    print("OK (Deleted)")
                else:
                    print(f"Error: {response.get('message')}")
                    
            elif cmd == "SET":
                if len(parts) < 3:
                    print("Usage: SET <key> <value>")
                    continue
                key = parts[1]
                value = parts[2]
                
                parsed_value = value
                try:
                    if (value.startswith('{') and value.endswith('}')) or (value.startswith('[') and value.endswith(']')):
                        parsed_value = json.loads(value)
                    elif '.' in value:
                        parsed_value = float(value)
                    else:
                        parsed_value = int(value)
                except ValueError:
                    pass
                except json.JSONDecodeError:
                    pass
                
                request = {"action": "SET", "key": key, "value": parsed_value}
                response = send_request(sock, request)
                if response.get("status") == "success":
                    print("OK")
                else:
                    print(f"Error: {response.get('message')}")
                    
            else:
                print(f"Unknown command: '{cmd}'. Type 'HELP' for available commands.")
                
    except KeyboardInterrupt:
        print("\nDisconnecting. Goodbye!")
    finally:
        sock.close()

if __name__ == "__main__":
    run_client()
