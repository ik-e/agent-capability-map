"""Postflight source rechecks, separate from timed discovery trials.

Captures public official documents and one read-only geocoding response. This
does not amend trial answers or establish station-ID/grid join success.
"""
import hashlib
import json
import re
from datetime import datetime, timezone
from html import unescape
from pathlib import Path
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'evals/runs/r0-2026-11-01-v2/postflight'
OUT.mkdir(parents=True, exist_ok=True)
SOURCES = {
    'od': 'https://data.seoul.go.kr/dataList/OA-21229/F/1/datasetView.do',
    'tdata-od': 'https://t-data.seoul.go.kr/dataprovide/trafficdataviewopenapi.do?data_id=1045',
    'tdata-station': 'https://t-data.seoul.go.kr/dataprovide/trafficdataviewopenapi.do?data_id=1044',
    'station': 'https://data.seoul.go.kr/dataList/OA-13252/F/1/datasetView.do',
    'master': 'https://data.seoul.go.kr/dataList/OA-21235/S/1/datasetView.do',
    'poi': 'https://www.data.go.kr/en/data/15083033/fileData.do',
    'population': 'https://data.seoul.go.kr/dataVisual/seoul/seoulLivingPopulation.do',
    'geocoding': 'https://open-meteo.com/en/docs/geocoding-api',
    'pyproj': 'https://pyproj4.github.io/pyproj/stable/api/transformer.html',
    'sjoin': 'https://geopandas.org/en/stable/docs/reference/api/geopandas.sjoin.html',
    'nominatim-policy': 'https://operations.osmfoundation.org/policies/nominatim/',
    'geocode-sample': 'https://geocoding-api.open-meteo.com/v1/search?name=Seoul&count=3&language=en&format=json&countryCode=KR',
}
records = []
for name, url in SOURCES.items():
    row = {'id': name, 'url': url, 'checked_at': datetime.now(timezone.utc).isoformat()}
    try:
        request = Request(url, headers={'User-Agent': 'AgentCapabilityMap-Research/0.1 (read-only pilot)'})
        with urlopen(request, timeout=25) as response:
            body = response.read(4_000_001)
            row.update(status=response.status, final_url=response.url,
                       content_type=response.headers.get('Content-Type'),
                       truncated=len(body) > 4_000_000,
                       sha256=hashlib.sha256(body).hexdigest(), bytes=len(body))
        content = body.decode('utf-8', errors='replace')
        if name == 'geocode-sample':
            parsed = json.loads(content)
            rows = parsed.get('results', [])
            row.update(returned_candidates=len(rows), valid_coordinates=bool(rows) and all(
                isinstance(r.get('latitude'), (float, int)) and isinstance(r.get('longitude'), (float, int))
                and -90 <= r['latitude'] <= 90 and -180 <= r['longitude'] <= 180 for r in rows),
                all_country_kr=bool(rows) and all(r.get('country_code') == 'KR' for r in rows),
                sample_results=rows,
                scope='Observed one unauthenticated place-name response; not station-ID matching, POI coverage, or OD/grid join.')
        else:
            content = re.sub(r'<(script|style)\b[^>]*>.*?</\1>', '', content, flags=re.S | re.I)
            content = unescape(re.sub(r'<[^>]+>', ' ', content))
            content = re.sub(r'\s+', ' ', content).strip()
            (OUT / (name + '.txt')).write_text(content, encoding='utf-8')
            row.update(text_chars=len(content), retrieval_only=True)
        (OUT / (name + '.raw')).write_bytes(body)
    except Exception as error:
        row['error'] = str(error)
    records.append(row)
    print(json.dumps({k: v for k, v in row.items() if k != 'sample_results'}, ensure_ascii=False), flush=True)
(OUT / 'sources.json').write_text(json.dumps(records, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
