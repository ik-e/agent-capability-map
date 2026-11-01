"""Read-only research boundary with durable atomic-action accounting.

Only HTTPS hosts explicitly configured by the operator can be opened. Search
uses Tavily when a key is supplied; no undocumented fallback search provider.
"""
import hashlib
import ipaddress
import json
import re
import socket
import time
import uuid
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urljoin, urlsplit
from urllib.request import Request, build_opener, HTTPRedirectHandler
from urllib.error import HTTPError

def now():
    return datetime.now(timezone.utc).isoformat()

class PageText(HTMLParser):
    def __init__(self):
        super().__init__(); self.parts=[]; self.links=[]; self.skip=0
    def handle_starttag(self, tag, attrs):
        if tag in ('script', 'style'): self.skip += 1
        if tag == 'a' and not self.skip:
            href = dict(attrs).get('href')
            if href: self.links.append(href)
    def handle_endtag(self, tag):
        if tag in ('script', 'style') and self.skip: self.skip -= 1
    def handle_data(self, value):
        if not self.skip and value.strip(): self.parts.append(value.strip())

class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None

class SearchNotConfigured(RuntimeError):
    pass

class ResearchRuntime:
    def __init__(self, log, budget, hosts, *, seconds=120, timeout=15, backend=None, search_key=None):
        self.log=Path(log); self.log.parent.mkdir(parents=True,exist_ok=True)
        if self.log.exists(): raise ValueError('Fresh log required; never overwrite an existing run')
        if budget < 0 or seconds <= 0: raise ValueError('Invalid budget')
        self.log.touch(exist_ok=False)
        self.budget=budget; self.used=0; self.hosts=set(hosts); self.timeout=timeout
        self.deadline=time.monotonic()+seconds; self.backend=backend; self.search_key=search_key
        self.documents={}; self.actions={}; self.links={}
        self.record({'event':'run_started','budget':budget,'seconds':seconds,'allowed_hosts':sorted(self.hosts),'search_ready':bool(search_key)})
    def record(self, value):
        with self.log.open('a',encoding='utf8') as stream:
            stream.write(json.dumps({'at':now(),**value},ensure_ascii=False)+'\n'); stream.flush()
    def check_url(self, url):
        parsed=urlsplit(url)
        if parsed.scheme != 'https' or parsed.hostname not in self.hosts or parsed.username or parsed.password or parsed.port not in (None,443):
            raise ValueError('URL outside explicit HTTPS allowlist')
        # Host resolution is checked at each redirect. OS TLS still validates the host.
        for address in socket.getaddrinfo(parsed.hostname,443,type=socket.SOCK_STREAM):
            if not ipaddress.ip_address(address[4][0]).is_global:
                raise ValueError('Non-public address prohibited')
        return url
    def request(self, url, event_id, *, data=None, headers=None):
        opener=build_opener(NoRedirect())
        for hop in range(6):
            self.check_url(url)
            if time.monotonic() >= self.deadline: raise TimeoutError('Run time budget exhausted')
            self.record({'event':'network_attempt','event_id':event_id,'hop':hop,'url':url,'method':'POST' if data else 'GET'})
            req=Request(url,data=data,headers={'User-Agent':'AgentCapabilityMap-Preflight/1.0',**(headers or {})})
            try:
                response=opener.open(req,timeout=min(self.timeout,max(.1,self.deadline-time.monotonic())))
            except HTTPError as error:
                if error.code in (301,302,303,307,308) and error.headers.get('Location') and data is None:
                    next_url=urljoin(url,error.headers['Location']); error.close(); url=next_url; continue
                raise
            with response:
                raw=response.read(1_048_577)
                if len(raw)>1_048_576: raise ValueError('Response exceeds one MiB limit')
                return {'status_code':response.status,'url':url,'content_type':response.headers.get('Content-Type',''),
                        'raw':raw.decode('utf8',errors='replace'),'raw_sha256':hashlib.sha256(raw).hexdigest(),'bytes':len(raw)}
        raise ValueError('Redirect limit exceeded')
    def perform(self, action, event_id):
        if self.backend: return self.backend(action, event_id)
        kind=action['kind']
        if kind=='query':
            if not self.search_key: raise SearchNotConfigured('Search provider not configured')
            response=self.request('https://api.tavily.com/search',event_id,
                data=json.dumps({'query':action['query'],'max_results':5,'search_depth':'basic'}).encode(),
                headers={'Authorization':'Bearer '+self.search_key,'Content-Type':'application/json'})
            return {'provider':'tavily','payload':json.loads(response['raw']),
                    'bytes':response['bytes'],'source_sha256':response['raw_sha256']}
        if kind in ('open','click'):
            url=action['url'] if kind=='open' else self.links[action['link_id']]
            response=self.request(url,event_id)
            if 'html' in response['content_type']:
                parser=PageText(); parser.feed(response['raw']); content='\n'.join(parser.parts)
                urls=list(dict.fromkeys(urljoin(response['url'],v) for v in parser.links))
            else: content=response['raw']; urls=[]
            doc_id='doc-'+uuid.uuid4().hex
            self.documents[doc_id]={'text':content,'url':response['url'],'source_event_id':event_id}
            links=[]
            for url in urls:
                parsed=urlsplit(url)
                if parsed.scheme=='https' and parsed.hostname in self.hosts and not parsed.username and not parsed.password:
                    ref='link-'+uuid.uuid4().hex; self.links[ref]=url; links.append({'link_id':ref,'url':url})
            return {'document_id':doc_id,'url':response['url'],'status_code':response['status_code'],
                    'text':content[:12000],'text_chars':len(content),'text_truncated':len(content)>12000,
                    'links':links[:30],'bytes':response['bytes'],'source_sha256':response['raw_sha256']}
        doc=self.documents[action['document_id']]; pattern=action['pattern']; text=doc['text']
        offsets=[]
        for match in re.finditer(re.escape(pattern),text,re.IGNORECASE):
            found=match.start()
            offsets.append({'offset':found,'excerpt':text[max(0,found-120):found+len(pattern)+240]})
            if len(offsets)>=10: break
        return {'document_id':action['document_id'],'source_event_id':doc['source_event_id'],
                'matches':offsets,'cache_only':True}
    def execute_batch(self, actions):
        if not isinstance(actions,list) or not 1<=len(actions)<=20: raise ValueError('Batch must contain 1..20 actions')
        for a in actions:
            kind=a.get('kind'); fields={'query':{'query'},'open':{'url'},'find':{'document_id','pattern'},'click':{'link_id'}}.get(kind)
            if fields is None or set(a)-fields-{'kind','retry_of'} or any(not isinstance(a.get(k),str) or not a[k] for k in fields):
                raise ValueError('Invalid atomic action')
            if any(len(a[k])>2000 for k in fields): raise ValueError('Action argument too long')
            if a.get('retry_of'):
                prior=self.actions.get(a['retry_of'])
                if not prior or {k:v for k,v in prior.items() if k!='retry_of'}!={k:v for k,v in a.items() if k!='retry_of'}:
                    raise ValueError('retry_of must reference the same prior action')
        if len(actions)>self.budget-self.used or time.monotonic()>=self.deadline:
            reason='budget_exhausted' if len(actions)>self.budget-self.used else 'time_exhausted'
            self.record({'event':'batch_rejected','reason':reason,'requested':len(actions),'remaining':self.budget-self.used})
            return {'status':'rejected','reason':reason,'results':[],'remaining':self.budget-self.used}
        results=[]
        for action in actions:
            if time.monotonic()>=self.deadline:
                self.record({'event':'batch_interrupted','reason':'time_exhausted','not_run':len(actions)-len(results)})
                return {'status':'interrupted','reason':'time_exhausted','results':results,'not_run':len(actions)-len(results),'remaining':self.budget-self.used}
            eid='action-'+uuid.uuid4().hex; started=time.monotonic(); self.used+=1; self.actions[eid]=dict(action)
            self.record({'event':'action_started','event_id':eid,'kind':action['kind'],'arguments':action,'ordinal':self.used})
            try:
                payload=self.perform(action,eid)
                encoded=json.dumps(payload,ensure_ascii=False,sort_keys=True).encode()
                digest=hashlib.sha256(encoded).hexdigest()
                # Response capture is private run data, never published automatically.
                artifact=self.log.parent/(eid+'.response.json'); artifact.write_bytes(encoded)
                row={'event_id':eid,'kind':action['kind'],'status':'ok','response_sha256':digest,
                     'response_artifact':artifact.name,'response_bytes':len(encoded),'source_url':payload.get('url'),'result':payload}
            except Exception as error:
                row={'event_id':eid,'kind':action['kind'],'status':'timeout' if isinstance(error,(TimeoutError,socket.timeout)) else 'error',
                     'error_type':type(error).__name__,'http_status':getattr(error,'code',None)}
            row['elapsed_seconds']=round(time.monotonic()-started,6)
            self.record({'event':'action_finished',**{k:v for k,v in row.items() if k!='result'}}); results.append(row)
        return {'status':'completed','results':results,'remaining':self.budget-self.used}
    def stop(self, reason):
        eid='stop-'+uuid.uuid4().hex
        self.record({'event':'stop','event_id':eid,'kind':'stop','status':'ok','reason':reason,'external_actions':self.used})
        return eid
