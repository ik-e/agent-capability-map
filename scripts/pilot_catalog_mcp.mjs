// Test-harness adapter only. It reads a frozen catalog and cannot execute tools.
import {readFile, realpath, appendFile} from 'node:fs/promises';
import path from 'node:path';
import {createInterface} from 'node:readline';
import {searchCatalog} from '../site/search-core.js';
const root=await realpath(process.argv[2]);
const logPath=process.argv[3];
async function read(relative){const file=await realpath(path.resolve(root,relative));if(!file.startsWith(root+path.sep))throw Error('Outside catalog snapshot');return JSON.parse(await readFile(file,'utf8'));}
const tools=[
 {name:'catalog.manifest',description:'Read the frozen public map manifest first.',inputSchema:{type:'object',properties:{}},annotations:{readOnlyHint:true}},
 {name:'catalog.browse',description:'Read root or child purpose categories and candidate IDs. Same graph as public UI.',inputSchema:{type:'object',properties:{category_id:{type:'string'}}},annotations:{readOnlyHint:true}},
 {name:'catalog.search',description:'Search frozen information/operation summaries with the public shared search logic.',inputSchema:{type:'object',required:['query'],properties:{query:{type:'string',maxLength:250},category_id:{type:'string'},record_kind:{enum:['operation','information_resource']},limit:{type:'integer',minimum:1,maximum:20}}},annotations:{readOnlyHint:true}},
 {name:'catalog.detail',description:'Read exactly one frozen record and its evidence references.',inputSchema:{type:'object',required:['kind','id'],properties:{kind:{enum:['operation','information_resource','binding','evidence']},id:{type:'string'}}},annotations:{readOnlyHint:true}}
];
async function call(name,args){
 if(process.argv[4] && process.argv[4]!=='catalog-first')throw Error('Catalog content is unavailable in this evaluation condition');
 if(name==='catalog.manifest')return read('manifest.json');
 const manifest=await read('manifest.json');
 if(name==='catalog.browse'){
  const browse=await read(manifest.browse_index);const index=await read(manifest.search_index);const selected=args.category_id||'';
  return {category_id:selected,categories:browse.categories.filter(c=>selected?(c.parent_ids||[]).includes(selected):!(c.parent_ids||[]).length),candidate_ids:selected?index.items.filter(i=>i.category_ids.includes(selected)).map(i=>i.id):[]};
 }
 if(name==='catalog.search'){
  if(typeof args.query!=='string'||args.query.length>250)throw Error('Invalid query');
  const index=await read(manifest.search_index);
  return searchCatalog(index.items,args.query,args.record_kind?{record_kind:args.record_kind}:{},args.category_id||'',args.limit||5);
 }
 if(name==='catalog.detail'){
  const dirs={operation:'operations',information_resource:'resources',binding:'bindings',evidence:'evidence'};
  if(!dirs[args.kind]||!/^\w+$/.test(args.id))throw Error('Invalid record reference');
  return read(dirs[args.kind]+'/'+args.id+'.json');
 }
 throw Error('Unknown tool');
}
const input=createInterface({input:process.stdin});
for await(const line of input){
 if(!line.trim())continue;
 let r;
 try{
  r=JSON.parse(line);let result;
  if(r.method==='initialize')result={protocolVersion:'2025-06-18',capabilities:{tools:{}},serverInfo:{name:'frozen-catalog-evaluation',version:'1'}};
  else if(r.method==='tools/list')result={tools};
  else if(r.method==='tools/call'){
   let value;let failed=false;try{value=await call(r.params.name,r.params.arguments||{});}catch(e){value={error:e.message};failed=true;}
   const text=JSON.stringify(value);result={content:[{type:'text',text}],isError:failed};
   if(logPath)await appendFile(logPath,JSON.stringify({at:new Date().toISOString(),tool:r.params.name,args:r.params.arguments||{},response_bytes:Buffer.byteLength(text),failed})+'\n');
  }
  else if(r.method?.startsWith('notifications/'))continue;
  else throw Error('Unsupported method');
  console.log(JSON.stringify({jsonrpc:'2.0',id:r.id,result}));
 }catch(e){if(r?.id!==undefined)console.log(JSON.stringify({jsonrpc:'2.0',id:r.id,error:{code:-32602,message:e.message}}));}
}
