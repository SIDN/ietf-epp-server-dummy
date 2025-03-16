import os
import io
from datetime import datetime
from model import loginType, createType, responseType, msgQType, creDataType, eppType, extAnyType, resultType, msgType, trIDType

script_dir = os.path.dirname(os.path.realpath(__file__))

namespace = {'epp': 'urn:ietf:params:xml:ns:epp-1.0', 'domain': 'urn:ietf:params:xml:ns:domain-1.0'}

def exec_epp(eppType):
   if eppType.command.login is not None:
   #if eppType.find(".//epp:login", namespaces=namespace) is not None:
       return login_(eppType.command.login)
   elif  eppType.command.create is not None:
      return create_(eppType.command.create.anytypeobjs_)

def login_(msg: loginType):
   #user = msg.clId
   #msg.find(".//epp:clID", namespaces=namespace).text
   print(f"login for user: {msg.clID}")

   return ok()

def create_(msg: createType):

   creData = creDataType(msg.name, crDate=datetime.now(), exDate=datetime.now())
   creData.name_nsprefix_ = 'domain'
   creData.set_ns_prefix_("domain")
   creData.original_tagname_ = "creData"
   creData.crDate_nsprefix_ = "domain"
   creData.exDate_nsprefix_ = "domain"
   
   
   any = extAnyType()
   any.set_anytypeobjs_([creData])
   
   response = responseType()
   response.set_resData(any)
   rmsg = msgType()
   rmsg.set_valueOf_("No Problemo")
   response.set_result([resultType(code=1000, msg=rmsg)])
   
   trId = trIDType(svTRID="my-server-id-1", clTRID=msg.parent_object_.parent_object_.clTRID)
   response.set_trID(trId)
   
   epp = eppType(response=response)
   
   output = io.StringIO()
   epp.export(output, 0)

   return output.getvalue()


def ok():
    with open(os.path.join(script_dir, 'xml' , 'response-1000.xml'), 'r') as file:
      response = file.read()
      return response
                        
                        
def error(code):
    with open(os.path.join(script_dir, 'xml' , f'response-{code}.xml'), 'r') as file:
      response = file.read()
      return response                      
                        