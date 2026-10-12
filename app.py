from flask import Flask, jsonify, render_template_string, request
from datetime import datetime, timezone
import subprocess, re

app = Flask(__name__)

PIPELINES = [
    {"id":"web-frontend","name":"Web Frontend","repo":"tg-web/frontend","branch":"main","status":"success","duration":"4m 18s","commit":"a91c2e7","author":"A. Sharma","updated":"2 min ago","progress":100},
    {"id":"api-gateway","name":"API Gateway","repo":"tg-platform/api-gateway","branch":"release/2026.10","status":"running","duration":"2m 04s","commit":"f82bb10","author":"R. Mehta","updated":"running","progress":68},
    {"id":"news-search","name":"News Search","repo":"search/news-indexer","branch":"develop","status":"failed","duration":"1m 32s","commit":"c44de12","author":"N. Iyer","updated":"18 min ago","progress":42},
    {"id":"mobile-app","name":"Mobile App","repo":"apps/mobile","branch":"main","status":"queued","duration":"—","commit":"b109a33","author":"P. Singh","updated":"queued","progress":0},
    {"id":"analytics","name":"Analytics ETL","repo":"data/analytics-etl","branch":"main","status":"success","duration":"8m 41s","commit":"91d18aa","author":"S. Rao","updated":"1 hr ago","progress":100},
]
ACTIVITY = [
    ("success","Web Frontend deployed to production","2 minutes ago","a91c2e7"),
    ("running","API Gateway build is running","3 minutes ago","f82bb10"),
    ("warning","News Search security scan found 2 high findings","18 minutes ago","c44de12"),
    ("info","Mobile App pipeline added to queue","26 minutes ago","b109a33"),
    ("success","Analytics ETL completed successfully","1 hour ago","91d18aa"),
]

def docker_info():
    try:
        p = subprocess.run(["docker","info","--format","{{.ServerVersion}}"],capture_output=True,text=True,timeout=3)
        if p.returncode == 0: return {"available":True,"version":p.stdout.strip() or "available"}
    except Exception: pass
    return {"available":False,"version":"Docker not detected"}

@app.route("/")
def home(): return render_template_string(HTML, docker=docker_info())

@app.route("/health")
def health():
    return {"status":"healthy","service":"interactive-cicd-dashboard","time":datetime.now(timezone.utc).isoformat()}

@app.route("/api/overview")
def overview():
    counts={k:sum(1 for p in PIPELINES if p["status"]==k) for k in ["success","running","failed","queued"]}
    return jsonify({"pipelines":PIPELINES,"activity":ACTIVITY,"counts":counts,"docker":docker_info(),"generated":datetime.now().strftime("%Y-%m-%d %H:%M:%S")})

@app.post("/api/pipeline/<pipeline_id>/run")
def run_pipeline(pipeline_id):
    for p in PIPELINES:
        if p["id"]==pipeline_id:
            p.update(status="running",progress=8,updated="started now",duration="0m 00s")
            ACTIVITY.insert(0,("running",f"{p['name']} pipeline started","just now",p["commit"]))
            return jsonify({"ok":True,"pipeline":p})
    return jsonify({"ok":False,"error":"Pipeline not found"}),404

@app.post("/api/pipeline")
def create_pipeline():
    data=request.get_json(silent=True) or {}
    name=(data.get("name") or "New Pipeline").strip()
    repo=(data.get("repo") or "team/new-repository").strip()
    branch=(data.get("branch") or "main").strip()
    pid=re.sub(r"[^a-z0-9]+","-",name.lower()).strip("-") or f"pipeline-{len(PIPELINES)+1}"
    p={"id":pid,"name":name,"repo":repo,"branch":branch,"status":"queued","duration":"—","commit":"new","author":"You","updated":"just now","progress":0}
    PIPELINES.insert(0,p); ACTIVITY.insert(0,("info",f"{name} pipeline created","just now","new"))
    return jsonify({"ok":True,"pipeline":p})

HTML = r'''
<!doctype html><html lang="en"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Pulse CI/CD Control Center</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
<style>
:root{--bg:#0b1120;--panel:#111a2e;--panel2:#17233b;--line:#263654;--text:#f7f9fc;--muted:#91a1bb;--blue:#5c8dff;--cyan:#38d9c5;--green:#54d68a;--red:#ff6b7a;--yellow:#f3c969;--shadow:0 18px 45px rgba(0,0,0,.22)}
*{box-sizing:border-box}body{margin:0;background:linear-gradient(135deg,#09101e,#0e172b 45%,#101d35);color:var(--text);font:14px Inter,Segoe UI,Arial,sans-serif}
.layout{display:grid;grid-template-columns:250px 1fr;min-height:100vh}.sidebar{padding:25px 18px;border-right:1px solid var(--line);background:#0b1425}
.brand{font-size:20px;font-weight:800;margin:0 0 30px}.brand span{color:var(--cyan)}
.nav a{display:flex;gap:12px;padding:12px 14px;border-radius:10px;color:var(--muted);text-decoration:none;margin:5px 0}.nav a.active,.nav a:hover{background:#1c2a48;color:#fff}
.sidebox{margin-top:35px;padding:15px;border:1px solid var(--line);border-radius:12px;background:#0f1b31}.sidebox small{color:var(--muted)}.dot{width:9px;height:9px;border-radius:50%;display:inline-block;background:var(--green);margin-right:7px}
main{padding:30px 34px;max-width:1700px;width:100%;margin:auto}.topbar{display:flex;justify-content:space-between;align-items:center;gap:15px}.eyebrow{color:var(--cyan);font-weight:700;letter-spacing:.08em;text-transform:uppercase;font-size:11px}.title{font-size:32px;margin:8px 0}.subtitle{color:var(--muted);margin:0}.actions{display:flex;gap:10px;flex-wrap:wrap}.btn{border:1px solid var(--line);border-radius:10px;padding:11px 15px;color:#fff;background:#172643;cursor:pointer;font-weight:700}.btn.primary{background:var(--blue);border-color:var(--blue)}.btn.ghost{background:transparent}
.grid{display:grid;gap:16px}.metrics{grid-template-columns:repeat(4,1fr);margin:28px 0 18px}.metric,.panel{background:linear-gradient(145deg,#121e35,#10192d);border:1px solid var(--line);border-radius:15px;box-shadow:var(--shadow)}.metric{padding:19px}.metric .label{color:var(--muted)}.metric .value{font-size:32px;font-weight:800;margin-top:9px}.metric .delta{color:var(--green);font-size:12px;margin-top:8px}
.two{grid-template-columns:1.7fr 1fr}.panel{padding:19px}.panelhead{display:flex;justify-content:space-between;align-items:center;margin-bottom:16px}.panel h2{font-size:16px;margin:0}.muted{color:var(--muted)}.tablewrap{overflow:auto}table{width:100%;border-collapse:collapse;min-width:680px}th,td{text-align:left;padding:13px 9px;border-bottom:1px solid var(--line);white-space:nowrap}th{color:var(--muted);font-size:11px;text-transform:uppercase;letter-spacing:.06em}.repo{font-weight:700}.sub{display:block;color:var(--muted);font-size:12px;margin-top:4px}.badge{border-radius:999px;padding:5px 9px;font-size:11px;font-weight:800;text-transform:uppercase}.success{color:#0a3b22;background:#8af0b4}.running{color:#082e3b;background:#75e8ec}.failed{color:#4a0c17;background:#ff9eaa}.queued{color:#4e3c08;background:#f5d77f}.progress{height:7px;background:#243451;border-radius:20px;overflow:hidden;min-width:90px}.bar{height:100%;background:linear-gradient(90deg,var(--blue),var(--cyan));border-radius:20px}
.activity{display:flex;gap:12px;padding:13px 0;border-bottom:1px solid var(--line)}.activity:last-child{border:0}.icon{width:28px;height:28px;border-radius:9px;display:grid;place-items:center;background:#1c2b47}.acttitle{font-weight:700}.chartbox{height:250px}.tag{padding:6px 9px;border-radius:8px;background:#1b2b49;color:#bcd0f3;font-size:12px}
.modal{position:fixed;inset:0;background:#050914aa;display:none;place-items:center;padding:20px}.modal.show{display:grid}.modalbox{width:min(500px,100%);background:#111a2e;border:1px solid var(--line);border-radius:16px;padding:24px}.modalbox input{width:100%;padding:12px;margin:7px 0 15px;border-radius:8px;border:1px solid var(--line);background:#0b1425;color:#fff}
@media(max-width:1050px){.layout{grid-template-columns:1fr}.sidebar{display:none}.metrics{grid-template-columns:repeat(2,1fr)}.two{grid-template-columns:1fr}}@media(max-width:600px){main{padding:20px 15px}.metrics{grid-template-columns:1fr}.topbar{align-items:flex-start;flex-direction:column}.title{font-size:25px}}
</style></head><body>
<div class="layout"><aside class="sidebar"><div class="brand">Pulse <span>CI/CD</span></div>
<nav class="nav"><a class="active" href="#">▦ Overview</a><a href="#pipelines">◈ Pipelines</a><a href="#deployments">⇧ Deployments</a><a href="#activity">◷ Activity</a><a href="#settings">⚙ Settings</a></nav>
<div class="sidebox"><div><span class="dot"></span>System operational</div><small>Last heartbeat: <span id="heartbeat">now</span></small></div>
<div class="sidebox"><small>Docker engine</small><h3 id="dockerState">{{ "Connected" if docker.available else "Not detected" }}</h3><small>{{ docker.version }}</small></div>
</aside><main>
<section class="topbar"><div><div class="eyebrow">Engineering operations</div><h1 class="title">CI/CD Control Center</h1><p class="subtitle">A live command view for builds, tests, security gates and deployments.</p></div><div class="actions"><button class="btn ghost" onclick="refresh()">↻ Refresh</button><button class="btn primary" onclick="openModal()">＋ New pipeline</button></div></section>
<section class="grid metrics"><div class="metric"><div class="label">Successful runs</div><div class="value" id="successCount">—</div><div class="delta">↑ 12.8% this week</div></div><div class="metric"><div class="label">Running now</div><div class="value" id="runningCount">—</div><div class="delta" style="color:var(--cyan)">● Live execution</div></div><div class="metric"><div class="label">Failed runs</div><div class="value" id="failedCount">—</div><div class="delta" style="color:var(--red)">Needs review</div></div><div class="metric"><div class="label">Deployment success</div><div class="value">96.4%</div><div class="delta">↑ 3.1% vs last month</div></div></section>
<section class="grid two"><div class="panel" id="pipelines"><div class="panelhead"><h2>Pipeline overview</h2><span class="tag">Auto-refresh 10s</span></div><div class="tablewrap"><table><thead><tr><th>Pipeline</th><th>Status</th><th>Progress</th><th>Duration</th><th>Commit</th><th>Action</th></tr></thead><tbody id="pipelineRows"></tbody></table></div></div>
<div class="panel"><div class="panelhead"><h2>Delivery velocity</h2><span class="muted">Last 7 days</span></div><div class="chartbox"><canvas id="velocityChart"></canvas></div></div></section>
<section class="grid two" style="margin-top:16px"><div class="panel" id="activity"><div class="panelhead"><h2>Recent activity</h2><span class="tag">Live feed</span></div><div id="activityList"></div></div>
<div class="panel" id="deployments"><div class="panelhead"><h2>Release health</h2><span class="muted">Production</span></div><div style="display:grid;gap:14px"><div><div style="display:flex;justify-content:space-between"><span>Build pass rate</span><b>98.1%</b></div><div class="progress"><div class="bar" style="width:98%"></div></div></div><div><div style="display:flex;justify-content:space-between"><span>Test coverage</span><b>86.7%</b></div><div class="progress"><div class="bar" style="width:87%"></div></div></div><div><div style="display:flex;justify-content:space-between"><span>Security gates</span><b>94.2%</b></div><div class="progress"><div class="bar" style="width:94%"></div></div></div><div><div style="display:flex;justify-content:space-between"><span>Deploy reliability</span><b>96.4%</b></div><div class="progress"><div class="bar" style="width:96%"></div></div></div></div></div></section>
<footer class="muted" style="padding:24px 0 5px">Pulse CI/CD • <a href="/health" style="color:var(--cyan)">Health endpoint</a> • <span id="updated">Loading…</span></footer>
</main></div>
<div class="modal" id="modal"><div class="modalbox"><div class="panelhead"><h2>Create pipeline</h2><button class="btn ghost" onclick="closeModal()">✕</button></div><label class="muted">Pipeline name</label><input id="newName" placeholder="Example: Content API"><label class="muted">Repository</label><input id="newRepo" placeholder="team/repository"><label class="muted">Branch</label><input id="newBranch" value="main"><div class="actions" style="justify-content:flex-end"><button class="btn ghost" onclick="closeModal()">Cancel</button><button class="btn primary" onclick="createPipeline()">Create pipeline</button></div></div></div>
<script>
let chart;const esc=x=>String(x??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
function openModal(){document.getElementById('modal').classList.add('show')}function closeModal(){document.getElementById('modal').classList.remove('show')}
async function refresh(){const d=await(await fetch('/api/overview',{cache:'no-store'})).json();document.getElementById('successCount').textContent=d.counts.success;document.getElementById('runningCount').textContent=d.counts.running;document.getElementById('failedCount').textContent=d.counts.failed;document.getElementById('updated').textContent='Updated '+d.generated;document.getElementById('heartbeat').textContent='just now';document.getElementById('dockerState').textContent=d.docker.available?'Connected':'Not detected';document.getElementById('pipelineRows').innerHTML=d.pipelines.map(p=>`<tr><td><span class="repo">${esc(p.name)}</span><span class="sub">${esc(p.repo)} • ${esc(p.branch)}</span></td><td><span class="badge ${esc(p.status)}">${esc(p.status)}</span></td><td><div style="display:flex;align-items:center;gap:8px"><div class="progress"><div class="bar" style="width:${p.progress}%"></div></div><span class="muted">${p.progress}%</span></div></td><td>${esc(p.duration)}</td><td><span class="tag">${esc(p.commit)}</span></td><td><button class="btn" style="padding:7px 10px" onclick="runPipeline('${esc(p.id)}')">▶ Run</button></td></tr>`).join('');document.getElementById('activityList').innerHTML=d.activity.map(a=>`<div class="activity"><div class="icon">${a[0]=='success'?'✓':a[0]=='running'?'↻':a[0]=='warning'?'!':'i'}</div><div><div class="acttitle">${esc(a[1])}</div><div class="muted">${esc(a[2])} • ${esc(a[3])}</div></div></div>`).join('');renderChart()}
function renderChart(){if(chart)chart.destroy();chart=new Chart(document.getElementById('velocityChart'),{type:'line',data:{labels:['Mon','Tue','Wed','Thu','Fri','Sat','Sun'],datasets:[{label:'Successful deployments',data:[8,11,9,15,12,18,16],borderColor:'#38d9c5',backgroundColor:'#38d9c522',fill:true,tension:.4},{label:'Failed runs',data:[2,1,3,1,2,1,1],borderColor:'#ff6b7a',tension:.4}]},options:{responsive:true,maintainAspectRatio:false,plugins:{legend:{labels:{color:'#91a1bb'}}},scales:{x:{ticks:{color:'#91a1bb'},grid:{color:'#263654'}},y:{ticks:{color:'#91a1bb'},grid:{color:'#263654'}}}}})}
async function runPipeline(id){await fetch('/api/pipeline/'+encodeURIComponent(id)+'/run',{method:'POST'});refresh()}
async function createPipeline(){const body={name:document.getElementById('newName').value,repo:document.getElementById('newRepo').value,branch:document.getElementById('newBranch').value};await fetch('/api/pipeline',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(body)});closeModal();refresh()}
refresh();setInterval(refresh,10000);
</script></body></html>
'''
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
