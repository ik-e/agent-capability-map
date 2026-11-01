"""Create a separate v2 runner; keep v1's frozen protocol and logs intact."""
from pathlib import Path
root=Path(__file__).resolve().parents[1]
source=(root/'scripts/run_r0_pilot.py').read_text(encoding='utf8')
source=source.replace('r0-2026-11-01-v1','r0-2026-11-01-v2').replace("ROOT/'scripts/run_r0_pilot.py'","ROOT/'scripts/run_r0_pilot_v2.py'")
source=source.replace("protocol['schedule']=schedule","protocol['schedule']=schedule\n protocol['adapter']='trial-only frozen-catalog read-only MCP, same schema in all conditions; B/C access denied; v1 file-access failures excluded from v2 comparison'\n protocol['input_hashes_adapter']=digest(ROOT/'scripts/pilot_catalog_mcp.mjs')")
old="""  return common+'''처음에는 workspace의 catalog/manifest.json부터 읽어라."""
new="""  return common+'''처음에는 catalog.manifest MCP 도구부터 읽고 catalog.browse와 catalog.search로 후보를 좁힌 뒤 catalog.detail로 필요한 상세·근거만 읽어라. 파일 읽기는 사용하지 마라. 시험용 어댑터는 배포본과 같은 동결 정적 카탈로그만 읽으며 외부 서비스를 실행하지 않는다. 이는 workspace의 catalog/manifest.json"""
assert old in source
source=source.replace(old,new)
# Remove the superseded file-reading instructions in the treatment paragraph.
source=source.replace('부터 읽어라. 이는 https://ik-e.github.io/agent-capability-map/ 의 동결된 정적 파일이며 HTTP와 별도로 workspace에 고정해 둔 사본이다. 작은 browse/index와 manifest의 search_index에서 후보를 좁히고 필요한 상세·Evidence만 읽어라. 전체 bulk dump 금지. 로컬 JS search-core.mjs의 searchCatalog를 사용해도 된다.','(https://ik-e.github.io/agent-capability-map/ 동결 사본)에 연결된다. 전체 bulk dump 금지.')
source=source.replace("  started=time.monotonic(); print('START '+folder.name,flush=True)","  args[args.index('--sandbox'):args.index('--sandbox')] = ['-c','mcp_servers.catalog.command=\"node\"','-c','mcp_servers.catalog.args='+json.dumps([str(ROOT/'scripts/pilot_catalog_mcp.mjs'),str(RUN/'catalog'),str(folder/'catalog-access.jsonl'),trial['condition']])]\n  started=time.monotonic(); print('START '+folder.name,flush=True)")
target=root/'scripts/run_r0_pilot_v2.py'
if target.exists():raise RuntimeError('v2 runner already exists')
target.write_text(source,encoding='utf8')
print(target)
