let chart=null,currentId=null, supabaseClient=null, cloudUser=null;
const $=id=>document.getElementById(id);
const cfg=window.CC_CONFIG||{};
const API=(cfg.API_BASE_URL||'').replace(/\/$/,'');

function payload(){return {id:currentId,name:$('name').value,date:$('date').value,time:$('time').value,place:$('place').value,lat:+$('lat').value,lon:+$('lon').value,tz:+$('tz').value,ayanamsa:$('ayan').value,notes:$('notes').value,tags:''}}
function localProfiles(){try{return JSON.parse(localStorage.getItem('cc_profiles')||'[]')}catch{return []}}
function setLocalProfiles(v){localStorage.setItem('cc_profiles',JSON.stringify(v))}
function cacheProfile(p){const ps=localProfiles();const i=ps.findIndex(x=>x.id===p.id);if(i>=0)ps[i]={...ps[i],...p,updated_at:p.updated_at||new Date().toISOString()};else ps.unshift({...p,updated_at:p.updated_at||new Date().toISOString()});setLocalProfiles(ps)}
function profileForCloud(p){return {id:p.id||crypto.randomUUID(),name:p.name,date:p.date,time:p.time,place:p.place,lat:p.lat,lon:p.lon,tz:p.tz,ayanamsa:p.ayanamsa||'Lahiri',notes:p.notes||'',tags:p.tags||'',archived:false,updated_at:new Date().toISOString()}}

async function api(url,opt={}){let headers={'Content-Type':'application/json',...(opt.headers||{})};if(supabaseClient){const {data}=await supabaseClient.auth.getSession();if(data.session)headers.Authorization='Bearer '+data.session.access_token}let r=await fetch(API+url,{...opt,headers});let j=await r.json();if(!r.ok)throw Error(j.error||'Request failed');return j}

async function initCloud(){
  if(!cfg.SUPABASE_URL||!cfg.SUPABASE_ANON_KEY||!window.supabase){updateSync('Local mode');return}
  supabaseClient=window.supabase.createClient(cfg.SUPABASE_URL,cfg.SUPABASE_ANON_KEY,{auth:{persistSession:true,autoRefreshToken:true,detectSessionInUrl:true}});
  const {data}=await supabaseClient.auth.getSession();cloudUser=data.session?.user||null;renderAuthState();
  supabaseClient.auth.onAuthStateChange((_e,session)=>{cloudUser=session?.user||null;renderAuthState();if(cloudUser)syncNow()});
}
function updateSync(text){$('syncStatus').textContent=text}
function renderAuthState(){
  updateSync(cloudUser?`Synced: ${cloudUser.email}`:'Local mode');
  $('authBox').textContent=cloudUser?`Cloud sync enabled for ${cloudUser.email}. Your charts are private to this account.`:'Cloud sync is optional. Sign in to synchronize charts between devices.';
  $('loginBtn').textContent=cloudUser?'Account':'Sign in';
  $('signOut').classList.toggle('hidden',!cloudUser);$('signIn').classList.toggle('hidden',!!cloudUser);$('signUp').classList.toggle('hidden',!!cloudUser);
}
function openAuth(){ $('authModal').classList.remove('hidden'); }
function closeAuth(){ $('authModal').classList.add('hidden'); }

async function syncNow(){
  if(!cloudUser||!supabaseClient)return;
  try{
    updateSync('Syncing…');
    const {data,error}=await supabaseClient.from('profiles').select('*').order('updated_at',{ascending:false});
    if(error)throw error;
    const remote=data||[], local=localProfiles(), byId=new Map(local.map(p=>[p.id,p]));
    for(const r of remote){const l=byId.get(r.id);if(!l||new Date(r.updated_at)>new Date(l.updated_at||0))byId.set(r.id,r)}
    for(const l of byId.values()){
      const r=remote.find(x=>x.id===l.id);
      if(!r||new Date(l.updated_at||0)>new Date(r.updated_at||0)){
        const row={...profileForCloud(l),user_id:cloudUser.id};delete row.created_at;
        const {error:e}=await supabaseClient.from('profiles').upsert(row,{onConflict:'id'});if(e)throw e;
      }
    }
    setLocalProfiles([...byId.values()].sort((a,b)=>new Date(b.updated_at||0)-new Date(a.updated_at||0)));
    await loadProfiles();updateSync('Synced');
  }catch(e){console.error(e);updateSync('Sync error');}
}

async function loadProfiles(){
  const q=$('search').value.toLowerCase();let ps=localProfiles().filter(p=>`${p.name} ${p.place||''} ${p.tags||''}`.toLowerCase().includes(q));
  $('profiles').innerHTML=ps.map(p=>`<div class="profile" data-id="${p.id}"><b>${escapeHtml(p.name)}</b><div class="muted">${p.date} ${p.time} · ${escapeHtml(p.place||'')}</div></div>`).join('')||'<div class="muted" style="padding:10px">No saved charts.</div>';
  document.querySelectorAll('.profile').forEach(x=>x.onclick=()=>loadProfile(x.dataset.id));
  $('profileListFull').innerHTML=ps.map(p=>`<div class="card" style="margin:8px 0"><b>${escapeHtml(p.name)}</b> · ${p.date} ${p.time} · ${escapeHtml(p.place||'')}</div>`).join('')||'<div class="muted">No records.</div>';
}
async function loadProfile(id){let p=localProfiles().find(x=>String(x.id)===String(id));if(!p)return;currentId=p.id;for(let k of ['name','date','time','place','lat','lon','tz','notes'])$(k).value=p[k]??'';$('ayan').value=p.ayanamsa||'Lahiri';show('dashboard');await calculate()}
async function calculate(){try{chart=await api('/api/chart',{method:'POST',body:JSON.stringify(payload())});renderSummary();renderChart();renderAnalysis();renderDashas();}catch(e){alert(e.message)}}
function renderSummary(){let p=chart.planets,a=chart.ascendant;$('summary').innerHTML=`<div class="stats"><div class="stat"><b>${a.sign} ${a.degree.toFixed(2)}°</b><span>Lagna</span></div><div class="stat"><b>${p.Moon.sign} ${p.Moon.degree.toFixed(2)}°</b><span>Moon sign</span></div><div class="stat"><b>${p.Sun.sign} ${p.Sun.degree.toFixed(2)}°</b><span>Sun sign</span></div><div class="stat"><b>${p.Moon.nakshatra.name} P${p.Moon.nakshatra.pada}</b><span>Moon nakshatra</span></div><div class="stat"><b>${p.Moon.nakshatra.nadi}</b><span>Nadi</span></div></div><p class="muted" style="margin-bottom:0">Swiss Ephemeris · ${chart.ayanamsa} ayanamsa · Whole-sign Vedic houses</p>`}
function renderChart(){let labels=['Aries','Taurus','Gemini','Cancer','Leo','Virgo','Libra','Scorpio','Sagittarius','Capricorn','Aquarius','Pisces'],asc=chart.ascendant.sign_index,house=[];for(let i=0;i<12;i++){let ang=-90+i*30,r=190,x=250+r*Math.cos(ang*Math.PI/180),y=250+r*Math.sin(ang*Math.PI/180);house.push(`<text x="${x}" y="${y}" text-anchor="middle">${i+1}: ${labels[(asc+i)%12].slice(0,3)}</text>`)}let planets=Object.entries(chart.planets).map(([k,v])=>{let i=v.house-1,ang=(-90+(i+.5)*30)*Math.PI/180,x=250+145*Math.cos(ang),y=250+145*Math.sin(ang);return `<text x="${x}" y="${y}" text-anchor="middle">${k.slice(0,2)}</text>`}).join('');$('chart').innerHTML=`<svg class="chart" viewBox="0 0 500 500"><rect x="45" y="45" width="410" height="410"/><line x1="45" y1="45" x2="455" y2="455"/><line x1="455" y1="45" x2="45" y2="455"/><line x1="250" y1="45" x2="250" y2="455"/><line x1="45" y1="250" x2="455" y2="250"/>${house.join('')}${planets}</svg>`}
function renderAnalysis(){let p=chart.planets;$('planetTable').innerHTML='<tr><th>Planet</th><th>Longitude</th><th>Sign</th><th>House</th><th>Nakshatra</th><th>Pada</th><th>Retro</th></tr>'+Object.entries(p).map(([k,v])=>`<tr><td>${k}</td><td>${v.longitude.toFixed(5)}°</td><td>${v.sign} ${v.degree.toFixed(2)}°</td><td>${v.house}</td><td>${v.nakshatra.name}</td><td>${v.nakshatra.pada}</td><td>${v.retrograde?'Yes':'No'}</td></tr>`).join('');$('houseTable').innerHTML='<tr><th>House</th><th>Sign</th><th>Lord</th><th>Planets</th></tr>'+chart.houses.map(h=>`<tr><td>${h.house}</td><td>${h.sign}</td><td>${h.lord}</td><td>${h.planets.join(', ')||'—'}</td></tr>`).join('');$('nakTable').innerHTML='<tr><th>Point</th><th>Nakshatra</th><th>Lord</th><th>Pada</th><th>Nadi</th><th>Gana</th><th>Yoni</th></tr>'+Object.entries(p).map(([k,v])=>`<tr><td>${k}</td><td>${v.nakshatra.name}</td><td>${v.nakshatra.lord}</td><td>${v.nakshatra.pada}</td><td>${v.nakshatra.nadi}</td><td>${v.nakshatra.gana}</td><td>${v.nakshatra.yoni}</td></tr>`).join('');$('yogaText').innerHTML=chart.yogas.length?chart.yogas.map(y=>`<p><b>${y.name}</b> — ${y.reason}</p>`).join(''):'<p>No conservative yoga rules matched the current chart.</p>';$('aspectTable').innerHTML='<tr><th>From</th><th>To</th><th>Type</th></tr>'+chart.aspects.map(a=>`<tr><td>${a.from}</td><td>${a.to}</td><td>${a.types.join(', ')}</td></tr>`).join('')}
async function renderDashas(){let d=await api('/api/dasha',{method:'POST',body:JSON.stringify({chart,birth_date:$('date').value})});$('dashaOut').innerHTML='<table class="tbl"><tr><th>Lord</th><th>Start</th><th>End</th><th>Years</th><th>Birth balance</th></tr>'+d.map(x=>`<tr><td>${x.lord}</td><td>${x.start}</td><td>${x.end}</td><td>${x.years}</td><td>${x.balance_at_birth?'Yes':''}</td></tr>`).join('')+'</table>'}

$('calc').onclick=calculate;
$('save').onclick=async()=>{try{const p=profileForCloud(payload());currentId=p.id;cacheProfile(p);if(cloudUser){const row={...p,user_id:cloudUser.id};delete row.created_at;const {error}=await supabaseClient.from('profiles').upsert(row,{onConflict:'id'});if(error)throw error;updateSync('Synced')}await loadProfiles();alert(cloudUser?'Profile saved and synchronized.':'Profile saved on this device.')}catch(e){alert(e.message)}};
$('search').oninput=loadProfiles;
$('newBtn').onclick=()=>{currentId=null;$('name').value='New Chart';$('date').value='';$('time').value='';$('place').value='';$('notes').value='';show('dashboard')};
$('vargaBtn').onclick=async()=>{if(!chart)return alert('Calculate a chart first.');let j=await api('/api/varga',{method:'POST',body:JSON.stringify({chart,varga:+$('vargaSelect').value})});$('vargaOut').innerHTML='<table class="tbl"><tr><th>Point</th><th>Varga sign index</th></tr>'+Object.entries(j.planets).map(([k,v])=>`<tr><td>${k}</td><td>${v.sign+1}</td></tr>`).join('')+`<tr><td>Ascendant</td><td>${j.ascendant+1}</td></tr></table>`};
$('report').onclick=async()=>{if(!chart)return alert('Calculate a chart first.');let p=payload();if(!p.id){p=profileForCloud(p);currentId=p.id;cacheProfile(p);if(cloudUser){const {error}=await supabaseClient.from('profiles').upsert({...p,user_id:cloudUser.id},{onConflict:'id'});if(error)throw error}}let j=await api('/api/report',{method:'POST',body:JSON.stringify({profile:p,chart})});window.open((API+j.url),'_blank')};
$('export').onclick=()=>{let p=payload();let b=new Blob([JSON.stringify(p,null,2)],{type:'application/json'});let a=document.createElement('a');a.href=URL.createObjectURL(b);a.download=(p.name||'chart')+'.json';a.click();URL.revokeObjectURL(a.href)};
$('loginBtn').onclick=()=>openAuth();$('closeAuth').onclick=closeAuth;
$('signIn').onclick=async()=>{if(!supabaseClient)return $('authMessage').textContent='Cloud sync is not configured in this deployment.';const {error}=await supabaseClient.auth.signInWithPassword({email:$('authEmail').value,password:$('authPassword').value});$('authMessage').textContent=error?error.message:'Signed in. Synchronizing…';if(!error)closeAuth()};
$('signUp').onclick=async()=>{if(!supabaseClient)return $('authMessage').textContent='Cloud sync is not configured in this deployment.';const {error}=await supabaseClient.auth.signUp({email:$('authEmail').value,password:$('authPassword').value});$('authMessage').textContent=error?error.message:'Account created. Check your email if confirmation is enabled.'};
$('signOut').onclick=async()=>{await supabaseClient.auth.signOut();closeAuth()};
function show(v){document.querySelectorAll('.view').forEach(x=>x.classList.add('hidden'));$(v).classList.remove('hidden');document.querySelectorAll('.nav button').forEach(x=>x.classList.toggle('active',x.dataset.view===v));$('title').textContent=v[0].toUpperCase()+v.slice(1)}
function escapeHtml(s){return String(s).replace(/[&<>'"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;',"'":'&#39;','"':'&quot;'}[c]))}
document.querySelectorAll('.nav button').forEach(b=>b.onclick=()=>show(b.dataset.view));
(async()=>{await initCloud();await loadProfiles()})();
