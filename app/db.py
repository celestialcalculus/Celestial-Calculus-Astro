import sqlite3, json, os, shutil, datetime
BASE=os.path.dirname(os.path.dirname(__file__)); DB=os.path.join(BASE,'data','celestial.sqlite3')
os.makedirs(os.path.dirname(DB),exist_ok=True)

def conn():
 c=sqlite3.connect(DB); c.row_factory=sqlite3.Row; return c

def init():
 c=conn(); c.executescript('''CREATE TABLE IF NOT EXISTS profiles(id INTEGER PRIMARY KEY AUTOINCREMENT,name TEXT NOT NULL,date TEXT NOT NULL,time TEXT NOT NULL,place TEXT,lat REAL,lon REAL,tz REAL,notes TEXT DEFAULT '',tags TEXT DEFAULT '',created_at TEXT,updated_at TEXT); CREATE TABLE IF NOT EXISTS settings(key TEXT PRIMARY KEY,value TEXT); CREATE TABLE IF NOT EXISTS reports(id INTEGER PRIMARY KEY AUTOINCREMENT,profile_id INTEGER,name TEXT,path TEXT,created_at TEXT);'''); c.commit(); c.close()

def list_profiles(q=''):
 c=conn(); rows=c.execute("SELECT * FROM profiles WHERE name LIKE ? OR place LIKE ? OR tags LIKE ? ORDER BY updated_at DESC",(f'%{q}%',f'%{q}%',f'%{q}%')).fetchall(); c.close(); return [dict(r) for r in rows]
def get_profile(i):
 c=conn(); r=c.execute('SELECT * FROM profiles WHERE id=?',(i,)).fetchone(); c.close(); return dict(r) if r else None
def save(p):
 now=datetime.datetime.now().isoformat(timespec='seconds'); c=conn()
 if p.get('id'):
  c.execute('UPDATE profiles SET name=?,date=?,time=?,place=?,lat=?,lon=?,tz=?,notes=?,tags=?,updated_at=? WHERE id=?',(p['name'],p['date'],p['time'],p.get('place',''),p['lat'],p['lon'],p.get('tz',5.5),p.get('notes',''),p.get('tags',''),now,p['id'])); i=p['id']
 else:
  cur=c.execute('INSERT INTO profiles(name,date,time,place,lat,lon,tz,notes,tags,created_at,updated_at) VALUES(?,?,?,?,?,?,?,?,?,?,?)',(p['name'],p['date'],p['time'],p.get('place',''),p['lat'],p['lon'],p.get('tz',5.5),p.get('notes',''),p.get('tags',''),now,now)); i=cur.lastrowid
 c.commit(); c.close(); return get_profile(i)
def delete(i):
 c=conn(); c.execute('DELETE FROM profiles WHERE id=?',(i,)); c.commit(); c.close()
def backup(path): shutil.copy2(DB,path)
init()
