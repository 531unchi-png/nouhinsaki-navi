#!/usr/bin/env python3
"""Resolve saved Google Maps share URLs into GPS coordinates without guessing."""
import json,re,time,urllib.request,urllib.parse,html,pathlib
page=pathlib.Path("index.html").read_text()
start=page.index("const DEFAULTS=")+len("const DEFAULTS=")
end=page.index("];",start)+1
# JavaScript object literals at the start of the array are not strict JSON.
# Extract each individual JSON-style record containing a Google Maps shortlink.
records=[]
for match in re.finditer(r'\{[^{}]*"id":"([^"]+)"[^{}]*"maplink":"(https://maps\.app\.goo\.gl/[^"]+)"[^{}]*\}',page[start:end]):
    records.append((match.group(1),match.group(2)))
out=pathlib.Path("map-coordinates.json")
try: data=json.loads(out.read_text())
except (FileNotFoundError,ValueError): data={}
data.setdefault("official-kyochu-fujii-001","35.7161694,138.4431802")
def coords(url,body):
    candidates=[urllib.parse.unquote(url),html.unescape(body)]
    patterns=[r'!3d(-?\d{1,2}\.\d+)!4d(-?\d{1,3}\.\d+)',r'@(-?\d{1,2}\.\d+),(-?\d{1,3}\.\d+)',r'(-?\d{1,2}\.\d+)%2[Cc](-?\d{1,3}\.\d+)']
    for source in candidates:
        for pat in patterns:
            m=re.search(pat,source)
            if m:
                lat,lon=map(float,m.groups())
                if 20<=lat<=46 and 122<=lon<=154:return f"{lat},{lon}"
    return None
for identifier,link in records:
    if identifier in data:continue
    try:
        req=urllib.request.Request(link,headers={"User-Agent":"Mozilla/5.0"})
        with urllib.request.urlopen(req,timeout=18) as response:
            final=response.url
            body=response.read(300000).decode("utf-8","ignore")
        result=coords(final,body)
        if result:
            data[identifier]=result
            print("Resolved",identifier,result)
        else: print("Unresolved",identifier,final[:120])
    except Exception as e:print("Failed",identifier,str(e)[:130])
    time.sleep(0.25)
out.write_text(json.dumps(data,ensure_ascii=False,indent=2,sort_keys=True)+"\n")
print(f"Resolved {len(data)} locations; {len(records)} shortlinks checked")
