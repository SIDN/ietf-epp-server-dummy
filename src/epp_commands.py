import os

script_dir = os.path.dirname(os.path.realpath(__file__))

namespace = {'epp': 'urn:ietf:params:xml:ns:epp-1.0', 'domain': 'urn:ietf:params:xml:ns:domain-1.0'}

def exec_epp(msg):
   if msg.find(".//epp:login", namespaces=namespace) is not None:
       return login_(msg)

def login_(msg):
    user = msg.find(".//epp:clID", namespaces=namespace).text
    print(f"user: {user}")

    return ok()


def ok():
    with open(os.path.join(script_dir, 'xml' , 'response-1000.xml'), 'r') as file:
      response = file.read()
      return response
                        
                        
                        
                        