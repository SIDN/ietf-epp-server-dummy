import socket
import threading
import xml.etree.ElementTree as ET
import xmlschema
from epp_commands import exec_epp
import os
from pprint import pprint

script_dir = os.path.dirname(os.path.realpath(__file__))

locations = {
    'urn:ietf:params:xml:ns:eppcom-1.0': os.path.join(script_dir, 'xsd', 'eppcom-1.0.xsd'),
    'urn:ietf:params:xml:ns:epp-1.0': os.path.join(script_dir, 'xsd', 'epp-1.0.xsd'),
    'urn:ietf:params:xml:ns:domain-1.0': os.path.join(script_dir, 'xsd', 'domain-1.0.xsd'),
    'urn:ietf:params:xml:ns:host-1.0': os.path.join(script_dir, 'xsd', 'host-1.0.xsd'),
    'urn:ietf:params:xml:ns:contact-1.0': os.path.join(script_dir, 'xsd', 'contact-1.0.xsd'),
    'urn:ietf:params:xml:ns:secDNS-1.1': os.path.join(script_dir, 'xsd', 'secDNS-1.1.xsd')
}

def handle_client(client_socket, address):
    print(f"Connection received from {address}")

    xsd_schema = None
    # Parse the XSD schema
    

    # Construct the full file path relative to the script's directory
    file_path = os.path.join(script_dir, 'xsd/epp.xsd')
    with open(file_path, 'r') as xsd_f:
        xsd_schema = xmlschema.XMLSchema(xsd_f, locations=locations)
    
    #xsd_schema = ET.XMLSchema(xsd_tree)

    
    # EPP Greeting message (example XML response)
    epp_greeting = """
    <?xml version="1.0" encoding="UTF-8"?>
    <epp xmlns="urn:ietf:params:xml:ns:epp-1.0">
        <greeting>
            <svID>Example EPP Server</svID>
            <svDate>2025-03-15T12:00:00Z</svDate>
            <svcMenu>
                <version>1.0</version>
                <lang>en</lang>
            </svcMenu>
            <dcp>
                <access>all</access>
                <statement>
                    <purpose>admin</purpose>
                    <recipient>public</recipient>
                    <retention>business</retention>
                </statement>
            </dcp>
        </greeting>
    </epp>
    """
    
    # Send greeting with EPP length prefix (4-byte network order integer)
    message = epp_greeting.encode('utf-8')
    client_socket.send(len(message).to_bytes(4, 'big') + message)
    
    while True:
        print('wait-for-data')
        try:
            # data = client_socket.recv(4)
            # if not data:
            #     print('no-data')
            #     break
            
            # Remove the 4-byte length prefix
            # Read the first 4 bytes (length prefix)
            length_prefix = client_socket.recv(4)
            if not length_prefix:
                return None
            message_length = int.from_bytes(length_prefix, 'big')
            print(f"Received EPP message length: {message_length}")
    
            # Read exactly message_length bytes
            data = b""
            while len(data) < message_length:
                packet = client_socket.recv(message_length - len(data))
                if not packet:
                    return None
                data += packet

            epp_message = data.decode('utf-8')
            #epp_message = data[4:].decode('utf-8')
            print(f"Received EPP message: {epp_message}")
            
            # Parse XML
            try:
                xml_request = epp_message.strip();
                root = ET.fromstring(xml_request)
                print(f"Parsed XML Root: {root.tag}")

                xsd_schema.validate(xml_request)
                print(f"{root} is valid according to {xsd_schema}")

                # Use the generated class method to parse the XML
                #loginObj = loginType.factory(root)
                #loginObj = loginType.factory()
                #loginObj.build(root)
                objs = xsd_schema.to_objects(xml_request,use_namespaces=True)
                obj_dict = xsd_schema.to_dict(xml_request)
                
                response = None
                #namespace = {'epp': 'urn:ietf:params:xml:ns:epp-1.0', 'domain': 'urn:ietf:params:xml:ns:domain-1.0'}
                #cmd = root.find(".//epp:login", namespaces=namespace)
                #if objs._children[0][0].local_name == 'login':
                #if cmd is not None:
                response = exec_epp(root)
                    
                
                pprint(obj_dict)

                #login_user = loginObj.get_clID().text
                #print(f"got login for user: {login_user}")
                
                # Example response processing
                
                print(f"Send EPP message: {response}")
                response_message = response.encode('utf-8')
                client_socket.send(len(response_message).to_bytes(4, 'big') + response_message)
                # with open('xml/response-1000.xml', 'r') as file:
                #     response = file.read()
                #     print(f"Send EPP message: {response}")

                #     response_message = response.encode('utf-8')
                #     client_socket.send(len(response_message).to_bytes(4, 'big') + response_message)

                
            except ET.ParseError as e:
                print(f"Error parsing EPP XML message: {e}")
        except ConnectionResetError:
            break
    
    print(f"Connection closed from {address}")
    client_socket.close()


def start_server(host='0.0.0.0', port=700):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((host, port))
    server.listen()
    print(f"EPP server listening on {host}:{port}")
    
    while True:
        client_socket, address = server.accept()
        client_handler = threading.Thread(target=handle_client, args=(client_socket, address))
        client_handler.start()

if __name__ == "__main__":
    start_server()
