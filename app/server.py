from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
import json, os, urllib.parse, mimetypes, argparse
from .engine import calc_chart, dasha_timeline, varga_sign
from .report import make_pdf
from . import db
ROOT=os.path.join(os.path.dirname(os.path.dirname(__file__)),'web')
class H(SimpleHTTPRequestHandler):
 def __init__(self,*a,**kw): super().__init__(*a,directory=ROOT,**kw)
 def send_json(self,obj,status=200):
  b=json.dumps(obj,ensure_ascii=False).encode(); self.send_response(status); self.send_header('Content-Type','application/json; charset=utf-8'); self.send_header('Access-Control-Allow-Origin', os.environ.get('CC_CORS_ORIGIN','*')); self.send_header('Access-Control-Allow-Headers','Content-Type, Authorization'); self.send_header('Access-Control-Allow-Methods','GET,POST,DELETE,OPTIONS'); self.send_header('Content-Length',str(len(b))); self.end_headers(); self.wfile.write(b)
 def do_OPTIONS(self):
  self.send_response(204); self.send_header('Access-Control-Allow-Origin', os.environ.get('CC_CORS_ORIGIN','*')); self.send_header('Access-Control-Allow-Headers','Content-Type, Authorization'); self.send_header('Access-Control-Allow-Methods','GET,POST,DELETE,OPTIONS'); self.end_headers()
 def do_GET(self):
  p=urllib.parse.urlparse(self.path)
  if p.path=='/api/health': return self.send_json({'ok':True,'app':'Celestial Calculus','version':'0.2.0','engine':'Swiss Ephemeris'})
  if p.path.startswith('/reports/'):
   fn=os.path.basename(p.path); path=os.path.join(ROOT,'reports',fn)
   if not os.path.isfile(path): return self.send_json({'error':'Report not found'},404)
   data=open(path,'rb').read(); self.send_response(200); self.send_header('Content-Type','application/pdf'); self.send_header('Content-Disposition',f'inline; filename="{fn}"'); self.send_header('Content-Length',str(len(data))); self.end_headers(); self.wfile.write(data); return
  if p.path=='/api/profiles': return self.send_json(db.list_profiles(urllib.parse.parse_qs(p.query).get('q',[''])[0]))
  if p.path.startswith('/api/profiles/'):
   return self.send_json(db.get_profile(int(p.path.split('/')[-1])) or {},404 if not db.get_profile(int(p.path.split('/')[-1])) else 200)
  return super().do_GET()
 def do_POST(self):
  n=int(self.headers.get('Content-Length','0')); data=json.loads(self.rfile.read(n) or '{}'); p=urllib.parse.urlparse(self.path).path
  try:
   if p=='/api/profiles': return self.send_json(db.save(data))
   if p=='/api/chart': return self.send_json(calc_chart(data))
   if p=='/api/dasha': return self.send_json(dasha_timeline(data['chart'],data['birth_date']))
   if p=='/api/report':
    profile=data['profile']; chart=data['chart']; out=os.path.join(ROOT,'reports',f"celestial-{profile.get('id','new')}.pdf"); make_pdf(chart,profile,out); return self.send_json({'path':out, 'url':'/reports/'+os.path.basename(out)})
   if p=='/api/varga':
    v=int(data['varga']); return self.send_json({'varga':v,'planets':{k:{'sign':varga_sign(x['longitude'],v)} for k,x in data['chart']['planets'].items()},'ascendant':varga_sign(data['chart']['ascendant']['longitude'],v)})
   if p=='/api/backup':
    path=data.get('path') or os.path.join(os.path.dirname(os.path.dirname(__file__)),'data','celestial-backup.sqlite3'); db.backup(path); return self.send_json({'path':path})
   if p.startswith('/api/profiles/') and p.endswith('/delete'):
    db.delete(int(p.split('/')[-2])); return self.send_json({'ok':True})
   self.send_json({'error':'Not found'},404)
  except Exception as e: self.send_json({'error':str(e)},400)
if __name__=='__main__':
 ap=argparse.ArgumentParser(); ap.add_argument('--host',default='127.0.0.1'); ap.add_argument('--port',type=int,default=int(os.environ.get('PORT','8765'))); args=ap.parse_args(); print(f'Celestial Calculus running at http://{args.host}:{args.port}'); ThreadingHTTPServer((args.host,args.port),H).serve_forever()
