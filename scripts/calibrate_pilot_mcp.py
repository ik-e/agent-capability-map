import json,subprocess,shutil
from pathlib import Path
root=Path(__file__).resolve().parents[1]
run=root/'evals/runs/catalog-mcp-calibration';run.mkdir(parents=True,exist_ok=True)
cli=shutil.which('codex.exe') or shutil.which('codex')
args=[cli,'--no-daemon','exec','--ignore-user-config','--model','gpt-6.1-sol','--sandbox','read-only','--skip-git-repo-check','--ephemeral','--json','-c','mcp_servers.catalog.command="node"','-c','mcp_servers.catalog.args='+json.dumps([str(root/'scripts/pilot_catalog_mcp.mjs'),str(root/'evals/runs/r0-2026-11-01-v1/catalog'),str(run/'access.jsonl')]),'-o',str(run/'answer.txt'),'-']
with (run/'events.jsonl').open('w',encoding='utf8') as out,(run/'stderr.log').open('w',encoding='utf8') as err:
 p=subprocess.run(args,input='Use only catalog.manifest. Report the catalog revision and information resource count. Do not search, read files, or answer a real evaluation task.',encoding='utf8',stdout=out,stderr=err,timeout=90)
print('exit',p.returncode)
if (run/'answer.txt').exists():print((run/'answer.txt').read_text(encoding='utf8'))
