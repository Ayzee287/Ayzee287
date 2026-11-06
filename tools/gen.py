"""Generate self-hosted profile charts from the GitHub API (needs `gh` logged in)."""
import json, subprocess, os
USER="Ayzee287"
def gh(*a): return json.loads(subprocess.check_output(["gh","api",*a],text=True))
out=os.path.join(os.path.dirname(__file__),"..","assets")
cal=gh("graphql","-f",'query={user(login:"%s"){contributionsCollection{totalCommitContributions contributionCalendar{totalContributions weeks{contributionDays{date contributionCount}}}}}}'%USER)["data"]["user"]["contributionsCollection"]
repos=[r for r in gh("users/%s/repos?per_page=100&type=owner"%USER) if not r["private"] and not r["fork"]]
langs={}
for r in repos:
    for k,v in gh("repos/%s/languages"%r["full_name"]).items(): langs[k]=langs.get(k,0)+v
THEMES={"dark":dict(bg="#0d1117",fg="#f0f3f6",mut="#9198a1",ramp=["#161b22","#0e4429","#006d32","#26a641","#39d353"],bar="#21262d"),
        "light":dict(bg="#f6f8fa",fg="#1f2328",mut="#59636e",ramp=["#e6eaee","#aceebb","#4ac26b","#2da44e","#116329"],bar="#d1d9e0")}
LC={"C#":"#8b5cf6","PowerShell":"#3b82f6","TypeScript":"#3178c6","HTML":"#e34c26","CSS":"#a855f7","JavaScript":"#f1e05a","Shell":"#4eaa25","Python":"#3776ab","Batchfile":"#c1f12e","Lua":"#000080"}
F="font-family=\"Segoe UI, Helvetica, Arial, sans-serif\""
def heat(t):
    days=[d for w in cal["contributionCalendar"]["weeks"] for d in w["contributionDays"]]
    mx=max(d["contributionCount"] for d in days) or 1
    s=[f'<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="260" viewBox="0 0 1200 260" role="img" aria-label="Contributions over the last year"><rect width="1200" height="260" rx="16" fill="{t["bg"]}"/>',
       f'<text x="40" y="52" {F} font-size="22" font-weight="600" fill="{t["fg"]}">{cal["contributionCalendar"]["totalContributions"]} contributions in the last year</text>',
       f'<text x="40" y="76" {F} font-size="14" fill="{t["mut"]}">{cal["totalCommitContributions"]} commits · public and private</text>']
    for i,w in enumerate(cal["contributionCalendar"]["weeks"]):
        for j,d in enumerate(w["contributionDays"]):
            c=d["contributionCount"]; lv=0 if c==0 else min(4,1+int(3*c/mx))
            s.append(f'<rect x="{40+i*21.2:.1f}" y="{98+j*21}" width="17" height="17" rx="3" fill="{t["ramp"][lv]}"><title>{d["date"]}: {c}</title></rect>')
    return "".join(s)+"</svg>"
def lang(t):
    tot=sum(langs.values()); items=sorted(langs.items(),key=lambda x:-x[1])[:6]
    s=[f'<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="{150+len(items)*34}" viewBox="0 0 1200 {150+len(items)*34}" role="img" aria-label="Languages across public repositories"><rect width="1200" height="{150+len(items)*34}" rx="16" fill="{t["bg"]}"/>',
       f'<text x="40" y="52" {F} font-size="22" font-weight="600" fill="{t["fg"]}">Languages</text>',
       f'<text x="40" y="76" {F} font-size="14" fill="{t["mut"]}">by code volume across public repositories</text>']
    x=40; W=1120
    s.append(f'<clipPath id="c"><rect x="40" y="96" width="{W}" height="12" rx="6"/></clipPath><g clip-path="url(#c)">')
    for k,v in items:
        w=W*v/tot; s.append(f'<rect x="{x:.1f}" y="96" width="{w:.1f}" height="12" fill="{LC.get(k,"#888")}"/>'); x+=w
    s.append('</g>')
    for i,(k,v) in enumerate(items):
        y=146+i*34
        s.append(f'<circle cx="48" cy="{y-5}" r="6" fill="{LC.get(k,"#888")}"/><text x="66" y="{y}" {F} font-size="16" fill="{t["fg"]}">{k}</text>'
                 f'<rect x="260" y="{y-12}" width="780" height="8" rx="4" fill="{t["bar"]}"/><rect x="260" y="{y-12}" width="{max(4,780*v/items[0][1]):.0f}" height="8" rx="4" fill="{LC.get(k,"#888")}"/>'
                 f'<text x="1160" y="{y}" text-anchor="end" {F} font-size="16" fill="{t["mut"]}">{100*v/tot:.1f}%</text>')
    return "".join(s)+"</svg>"
for n,t in THEMES.items():
    open(f"{out}/activity-{n}.svg","w",encoding="utf-8").write(heat(t))
    open(f"{out}/languages-{n}.svg","w",encoding="utf-8").write(lang(t))
print(sorted(langs.items(),key=lambda x:-x[1])[:6])
