import json, sqlite3, time, threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlsplit, parse_qs
from pathlib import Path

DB='/data/network_guardian.db'
class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        # HA ingress proxy source; do not expose directly on LAN.
        if self.client_address[0] != '172.30.32.2':
            self.send_error(403); return
        path=urlsplit(self.path)
        try:
            if path.path.rstrip('/') in ('', '/index.html'):
                body=Path('/app/dashboard.html').read_bytes(); kind='text/html; charset=utf-8'
            elif path.path.endswith('/api/data'):
                p=parse_qs(path.query); client=p.get('client',[''])[0]; search=p.get('search',[''])[0]
                with sqlite3.connect('file:'+DB+'?mode=ro',uri=True,timeout=5) as c:
                    c.row_factory=sqlite3.Row
                    def rows(sql,args=()): return [dict(r) for r in c.execute(sql,args)]
                    now=time.time(); cutoff=now-86400
                    result={'now':now,'summary':rows('SELECT COUNT(*) total, COALESCE(SUM(blocked),0) blocked, COUNT(DISTINCT client) clients, COUNT(DISTINCT domain) domains FROM dns_queries WHERE epoch>=?',(cutoff,))[0], 'devices':rows('SELECT client,COUNT(*) total,SUM(blocked) blocked,COUNT(DISTINCT domain) domains,MIN(epoch) first_seen,MAX(epoch) last_seen FROM dns_queries GROUP BY client ORDER BY total DESC'), 'live':rows('SELECT timestamp,client,domain,query_type,reason,blocked FROM dns_queries WHERE (?=\'\' OR client=?) AND instr(domain,?)>0 ORDER BY epoch DESC LIMIT 200',(client,client,search.lower())) if search else rows('SELECT timestamp,client,domain,query_type,reason,blocked FROM dns_queries WHERE (?=\'\' OR client=?) ORDER BY epoch DESC LIMIT 200',(client,client)), 'domains':rows('SELECT domain,COUNT(*) total,SUM(blocked) blocked,COUNT(DISTINCT client) clients FROM dns_queries WHERE (?=\'\' OR client=?) AND instr(domain,?)>0 GROUP BY domain ORDER BY total DESC LIMIT 200',(client,client,search.lower())) if search else rows('SELECT domain,COUNT(*) total,SUM(blocked) blocked,COUNT(DISTINCT client) clients FROM dns_queries WHERE (?=\'\' OR client=?) GROUP BY domain ORDER BY total DESC LIMIT 200',(client,client)), 'events':rows('SELECT * FROM security_events ORDER BY timestamp DESC LIMIT 200'), 'hours':rows('SELECT CAST(epoch/3600 AS INTEGER)*3600 hour,COUNT(*) total,SUM(blocked) blocked FROM dns_queries WHERE epoch>=? GROUP BY hour ORDER BY hour',(cutoff,))}
                result['learning_days']=json.loads(Path('/data/options.json').read_text()).get('learning_days',7)
                body=json.dumps(result).encode(); kind='application/json'
            else: self.send_error(404); return
            self.send_response(200); self.send_header('Content-Type',kind); self.send_header('Cache-Control','no-store'); self.send_header('X-Content-Type-Options','nosniff'); self.send_header('Content-Length',str(len(body))); self.end_headers(); self.wfile.write(body)
        except Exception as e:
            print('[DASHBOARD]',e,flush=True); self.send_error(500)
    def log_message(self,*args): pass

def start_dashboard():
    server=ThreadingHTTPServer(('0.0.0.0',8099),Handler)
    threading.Thread(target=server.serve_forever,daemon=True).start()
    print('[DASHBOARD] Ingress server listening on 8099',flush=True)
