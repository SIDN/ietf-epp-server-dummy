import socket
import threading
import xml.etree.ElementTree as ET
import xmlschema
from epp_commands import exec_epp, error
import os
from pprint import pprint
from model import parseString

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
    print(f'load main XSD from: {file_path}')
    print(f'Use XSD locations: {locations}')
    
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
        try:
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
            print(f"Received EPP message: {epp_message}")
            
            # Parse XML
            try:
                xml_request = epp_message.strip();
               
                if not validate(xsd_schema, xml_request):
                    response = error(2001)
                else:
                    print(f"XML is valid according to {xsd_schema}")
                    root = None
                    try:
                        root = ET.fromstring(xml_request)
                        objs = xsd_schema.to_objects(xml_request,use_namespaces=True)
                        obj_dict = xsd_schema.to_dict(xml_request)
                        
                        eppType = parseString(xml_request)
                        response = exec_epp(eppType)
                    except Exception as ex:
                        print(ex)
                        response = error(2001)

                print(f"Send EPP message: {response}")
                response_message = response.encode('utf-8')
                client_socket.send(len(response_message).to_bytes(4, 'big') + response_message)
                
            except ET.ParseError as e:
                print(f"Error parsing EPP XML message: {e}")
        except ConnectionResetError:
            break
    
    print(f"Connection closed from {address}")
    client_socket.close()

def validate(xsd_schema, xml):
    try:
        xsd_schema.validate(xml)
        # if not valid:
        #     print("XML is NOT valid!")
        #     for error in xsd_schema.error_log:
        #         print(f"Line {error.line}: {error.message}")
                
        return True
    except Exception as ex:
        print(f'Validation error: {ex}')
        return False

def start_server(host='0.0.0.0', port=7001):
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
