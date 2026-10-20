"""Owned loopback transport fixture; never contacts an account or model."""
import http.server,json,pathlib,sys,threading,time
root=pathlib.Path(sys.argv[1]);root.mkdir(exist_ok=True)
class Fixture(http.server.BaseHTTPRequestHandler):
 def log_message(self,*args):pass
 def do_POST(self):
  try:
   body=json.loads(self.rfile.read(int(self.headers['Content-Length'])))
   assert self.path=='/responses' and self.headers.get('Authorization') is None
   assert body['tools']==[] and body['store'] is False and body['parallel_tool_calls'] is False
   content=json.loads(body['input'][0]['content'])
   assert content['kind']=='helper-global-chat' and content['projectId']==''
   assert content['context']['projectId']=='' and content['context']['membership']['kind']=='global'
   assert all(m['scope']=='common' for m in content['context']['memory'])
   assert not any(s in json.dumps(body) for s in ['PROJECT PRIVATE','LEGACY PRIVATE','toolCapability','authorization','credentialReference'])
   with (root/'requests.jsonl').open('a') as f:f.write(json.dumps(body)+'\n')
   if content['message']=='wait-global':
    (root/'waiting').touch();deadline=time.monotonic()+15
    while not (root/'release').exists() and time.monotonic()<deadline:time.sleep(.01)
   if content['message']=='fail-global' and not (root/'allow-retry').exists():self.send_response(429);self.end_headers();return
   text='OWNED GLOBAL HTTP FIXTURE: '+content['context']['helper']+' / '+content['message']
   data=json.dumps({'status':'completed','output':[{'type':'message','role':'assistant','content':[{'type':'output_text','text':text}]}]}).encode()
   self.send_response(200);self.send_header('Content-Type','application/json');self.send_header('Content-Length',str(len(data)));self.end_headers();self.wfile.write(data)
  except (BrokenPipeError,ConnectionResetError):pass
  except BaseException as error:
   (root/'error').write_text(repr(error));self.send_error(500)
server=http.server.ThreadingHTTPServer(('127.0.0.1',0),Fixture)
print('http://127.0.0.1:'+str(server.server_port)+'/responses',flush=True)
server.serve_forever()
