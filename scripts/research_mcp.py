"""Trial-only stdio MCP; not a hosted product API or a browser controller."""
import argparse
import json
import os
import sys
from research_runtime import ResearchRuntime

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--log',required=True); parser.add_argument('--hosts',nargs='+',required=True)
    parser.add_argument('--budget',type=int,default=12); parser.add_argument('--seconds',type=int,default=300)
    args=parser.parse_args()
    hosts=args.hosts+(['api.tavily.com'] if os.environ.get('TAVILY_API_KEY') else [])
    runtime=ResearchRuntime(args.log,args.budget,hosts,seconds=args.seconds,search_key=os.environ.get('TAVILY_API_KEY'))
    tools=[{'name':'research.batch','description':'Execute 1..20 individually metered query/open/find/click actions. Whole batch is rejected if over remaining budget. Query requires configured Tavily access; open/click require operator allowlisted HTTPS hosts.',
            'inputSchema':{'type':'object','additionalProperties':False,'required':['actions'],'properties':{'actions':{'type':'array','minItems':1,'maxItems':20,'items':{'type':'object','properties':{'kind':{'enum':['query','open','find','click']},'query':{'type':'string'},'url':{'type':'string'},'document_id':{'type':'string'},'pattern':{'type':'string'},'link_id':{'type':'string'},'retry_of':{'type':'string'}},'required':['kind'],'additionalProperties':False}}}},'annotations':{'readOnlyHint':True}}]
    for line in sys.stdin:
        request={}
        try:
            request=json.loads(line); method=request.get('method'); params=request.get('params',{})
            if method=='initialize':
                result={'protocolVersion':'2025-06-18','capabilities':{'tools':{}},'serverInfo':{'name':'metered-research-preflight','version':'1'}}
            elif method=='tools/list': result={'tools':tools}
            elif method=='tools/call':
                if params.get('name')!='research.batch': raise ValueError('Unknown tool')
                value=runtime.execute_batch(params.get('arguments',{}).get('actions'))
                result={'content':[{'type':'text','text':json.dumps(value,ensure_ascii=False)}]}
            elif method.startswith('notifications/'): continue
            else: raise ValueError('Unsupported method')
            response={'jsonrpc':'2.0','id':request.get('id'),'result':result}
        except Exception as error:
            response={'jsonrpc':'2.0','id':request.get('id'),'error':{'code':-32602,'message':type(error).__name__}}
        print(json.dumps(response,ensure_ascii=False),flush=True)

if __name__=='__main__': main()
