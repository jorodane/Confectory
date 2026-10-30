"""Owned loopback Responses fixture over the production provider's public HTTP/tool protocol.

No provider substitution, credential, external service, or product-only test branch.
"""
import http.server,json,threading
class OwnedResponses:
 def __init__(self,target,node_source="return value + 5;"):
  self.target=target;self.node_source=node_source;self.requests=[];self.errors=[];fixture=self
  class Handler(http.server.BaseHTTPRequestHandler):
   def log_message(self,*args):pass
   def do_POST(self):
    try:
     assert self.path=='/responses' and self.headers.get('Authorization') is None
     size=int(self.headers['Content-Length']);assert size<=262144
     body=json.loads(self.rfile.read(size));fixture.requests.append(body)
     assert body['store'] is False and body['parallel_tool_calls'] is False
     serialized=json.dumps(body);assert 'toolCapability' not in serialized and 'credentialReference' not in serialized and 'authorization' not in serialized
     request=json.loads(body['input'][0]['content']);project=request['projectId'];node_task=(request.get('task') or {}).get('specification',{}).get('kind')=='blueprint-node'
     if node_task:
      assert request['context'] is None
      assert request['task']['specification']['blueprintNode']['assignment']['id']==fixture.target
      assert {tool['name'] for tool in body['tools']}=={'workspace_list','workspace_read','workspace_stage','workspace_changes'}
      for tool in body['tools']:
       if 'id' in tool['parameters']['properties']:assert tool['parameters']['properties']['id']['enum']==[fixture.target]
     else:assert request['context']['projectId']==project
     tools={item['name'] for item in body['tools']};assert request['kind']!='worker-task' or 'workspace_stage' in tools
     def message(text):return {'type':'message','role':'assistant','content':[{'type':'output_text','text':text}]}
     def call(name,args):return {'type':'function_call','call_id':'owned-'+name,'name':name,'arguments':json.dumps(args)}
     outputs=[item for item in body['input'] if item.get('type')=='function_call_output']
     if request['kind']!='worker-task':
      assert request['message']
      cards=[{'title':'Owned protocol card '+str(n),'summary':'Stage one owned body for explicit human review','rarity':'standard','effort':'small','risk':'low','tags':['owned-loopback','draft'],'changes':[]} for n in range(3)]
      output=message(json.dumps({'cards':cards}))
     elif not outputs:output=call('workspace_read',{'projectId':project,'id':fixture.target})
     elif len(outputs)==1:
      unit=json.loads(outputs[0]['output'])
      if node_task:
       record=json.loads(unit['text']);record['definitionHash']=unit['assignment']['definitionHash'];record['source']=fixture.node_source
       output=call('workspace_stage',{'projectId':project,'id':fixture.target,'expectedRevision':unit['revision'],'expectedHash':unit['textHash'],'text':json.dumps(record)})
      else:output=call('workspace_stage',{'projectId':project,'id':fixture.target,'expectedRevision':unit['revision'],'text':unit['text']+'\n// owned HTTP Worker draft; human review required\n'})
     else:
      assert json.loads(outputs[-1]['output'])['applied'] is True
      output=message('Owned protocol Worker staged source. Human review and explicit outcome evidence required.')
     response=json.dumps({'status':'completed','output':[output]}).encode();self.send_response(200);self.send_header('Content-Type','application/json');self.send_header('Content-Length',str(len(response)));self.end_headers();self.wfile.write(response)
    except Exception as error:
     fixture.errors.append(repr(error));self.send_error(500)
  self.server=http.server.ThreadingHTTPServer(('127.0.0.1',0),Handler);self.thread=threading.Thread(target=self.server.serve_forever,daemon=True);self.thread.start();self.endpoint='http://127.0.0.1:'+str(self.server.server_port)+'/responses'
 def close(self):self.server.shutdown();self.server.server_close();self.thread.join(timeout=3)
