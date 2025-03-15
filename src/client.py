import socket
import xml.etree.ElementTree as ET

def receive_message(sock):
    # Read the first 4 bytes for the length prefix
    length_prefix = sock.recv(4)
    if not length_prefix:
        return None
    message_length = int.from_bytes(length_prefix, 'big')
    
    # Read the full message
    data = sock.recv(message_length)
    return data.decode('utf-8')

def send_epp_request(sock, xml_request):
    print(f"send: {xml_request}")
    message = xml_request.encode('utf-8')
    sock.send(len(message).to_bytes(4, 'big') + message)

def main():
    host = 'localhost'
    port = 700
    
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((host, port))
    print(f"Connected to EPP server at {host}:{port}")
    
    # Receive greeting
    greeting = receive_message(client_socket)
    if greeting:
        print("Received EPP Greeting:")
        print(greeting)
    else:
        print("No greeting received.")
        return
    
    # Example EPP Login Request
    epp_login = """
    <?xml version="1.0" encoding="UTF-8"?>
    <epp xmlns="urn:ietf:params:xml:ns:epp-1.0">
        <command>
            <login>
                <clID>example-client</clID>
                <pw>12345678</pw>
                <options>
                    <version>1.0</version>
                    <lang>en</lang>
                </options>
                <svcs>
                    <objURI>urn:ietf:params:xml:domain-1.0</objURI>
                </svcs>
            </login>
            <clTRID>ABC-12345</clTRID>
        </command>
    </epp>
    """
    
    send_epp_request(client_socket, epp_login)
    
    # Receive response
    response = receive_message(client_socket)
    if response:
        print("Received EPP Response:")
        print(response)
        
        # Parse XML Response
        try:
            root = ET.fromstring(response)
            print(f"Parsed Response Root: {root.tag}")
        except ET.ParseError:
            print("Error parsing EPP XML response")
    else:
        print("No response received.")
    
    client_socket.close()
    print("Connection closed.")

if __name__ == "__main__":
    main()
