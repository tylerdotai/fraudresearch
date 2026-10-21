"""Catalog-discovered national CMS and OIG inputs. No name matching or fraud classification."""
from __future__ import annotations

import json
import re
import time
import zipfile
from html.parser import HTMLParser
from pathlib import Path
from typing import Any
from urllib.parse import urlencode, urljoin, urlsplit

import httpx

from . import now
from .bulk import acquire, convert, raw_verified, save


class Links(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.links: list[str] = []

    def handle_starttag(self, tag: str, attrs: Any) -> None:
        if tag == 'a':
            href = dict(attrs).get('href')
            if href:
                self.links.append(href)


def json_original(raw: dict[str, Any]) -> Any:
    return json.loads(Path(raw['path']).read_text())


def connector(root: Path, name: str, max_bytes: int, max_rows: int) -> dict[str, Any]:
    if not 0 < max_bytes <= 5_000_000_000 or not 0 < max_rows <= 50_000_000:
        raise ValueError('Connector byte/row budget invalid')
    audit: dict[str, Any] = {'connector': name, 'state': 'discovering', 'at': now()}
    try:
        catalog_ids = []
        jobs: list[tuple[str, list[str], str | None, str]] = []
        if name.startswith('cms-'):
            slug = 'hospice-enrollments' if name == 'cms-hospice-enrollments' else 'hospice-all-owners'
            slug_url = 'https://data.cms.gov/data-api/v1/slug?' + urlencode({
                'path': '/provider-characteristics/hospitals-and-other-facilities/' + slug})
            catalog = acquire(root, slug_url, min(max_bytes, 2000000))
            catalog_ids.append(catalog['id'])
            current = json_original(catalog)['data']['current_dataset']
            uuid = current['uuid']
            if not re.fullmatch('[0-9a-f-]{36}', uuid):
                raise ValueError('CMS current dataset UUID drift')
            resources = acquire(root, 'https://data.cms.gov/data-api/v1/dataset/' + uuid + '/resources',
                                min(max_bytes, 2000000))
            catalog_ids.append(resources['id'])
            items = json_original(resources)['data']
            kind = 'Report' if name == 'cms-hospice-chow' else 'Primary'
            selected = [x for x in items if x['type'] == kind and
                        (name != 'cms-hospice-chow' or 'Change of Ownership' in x.get('title', ''))]
            if len(selected) != 1:
                raise ValueError('CMS expected unique resource missing; review catalog drift')
            item = selected[0]
            if name == 'cms-hospice-chow':
                archive = acquire(root, item['file_url'], max_bytes)
                catalog_ids.append(archive['id'])
                with zipfile.ZipFile(archive['path']) as z:
                    members = [i.filename for i in z.infolist() if
                               re.fullmatch(r'Hospice_CHOW_[0-9.]+\.csv', i.filename)]
                if len(members) != 1:
                    raise ValueError('CMS CHOW archive transaction member drift')
                jobs.append((archive['id'], ['ENROLLMENT ID - BUYER', 'ENROLLMENT ID - SELLER',
                                            'CCN - BUYER', 'EFFECTIVE DATE'], members[0], 'latin-1'))
            else:
                raw = acquire(root, item['file_url'], max_bytes)
                required = ['ENROLLMENT ID', 'ASSOCIATE ID']
                required += ['ASSOCIATE ID - OWNER', 'PERCENTAGE OWNERSHIP'] if name.endswith('owners') else ['NPI', 'CCN']
                jobs.append((raw['id'], required, None, 'latin-1'))
                if name == 'cms-hospice-enrollments':
                    extra = [x for x in items if x.get('title') == 'Hospice Additional NPIs']
                    if len(extra) != 1:
                        raise ValueError('CMS additional NPI companion missing; do not assume one NPI/enrollment')
                    other = acquire(root, extra[0]['file_url'], max_bytes)
                    jobs.append((other['id'], ['ENROLLMENT ID', 'NPI'], None, 'latin-1'))
            coverage = ('Current published Medicare hospice enrollment/ownership snapshot ' + current['version'] +
                        '; self-reported, not a historical census or evidence of billing. CHOW not necessarily majority transfer.')
        else:
            url = 'https://oig.hhs.gov/exclusions/leie-database-supplement-downloads/'
            catalog = acquire(root, url, min(max_bytes, 2000000))
            catalog_ids.append(catalog['id'])
            parser = Links()
            parser.feed(Path(catalog['path']).read_text(encoding='utf-8-sig'))
            links = sorted({urljoin(url, x) for x in parser.links})
            if name == 'oig-leie':
                selected_urls = [x for x in links if urlsplit(x).path.endswith('/UPDATED.csv')]
            else:
                candidates = [(m.group(1), m.group(2), x) for x in links
                              if (m := re.search(r'/([0-9]{4})/([0-9]{4})rein\.csv$', x))]
                selected_urls = [max(candidates)[2]] if candidates else []
            if len(selected_urls) != 1:
                raise ValueError('OIG expected unique/latest catalog resource absent')
            raw = acquire(root, selected_urls[0], max_bytes)
            jobs.append((raw['id'], ['NPI', 'EXCLDATE', 'REINDATE', 'WAIVERDATE', 'WVRSTATE'], None, 'utf-8-sig'))
            coverage = ('Current active exclusion snapshot only; not full historical intervals' if name == 'oig-leie'
                        else 'Latest published monthly reinstatement supplement only; not complete reinstatement history')
        datasets = []
        for sid, required, member, encoding in jobs:
            raw_verified(root, sid)
            datasets.append(convert(root, sid, member, required, encoding, max_rows, 200000000))
        audit.update(state='exercised', catalog_id=catalog_ids[0], catalog_ids=catalog_ids,
                     datasets=datasets, coverage=coverage,
                     encoding_note=('CMS latin-1 is reversible structural decoding; publisher encoding unconfirmed; '
                                    'do not use decoded names for identity without validation'),
                     inferred_fraud=False, historical_completeness=False)
        return audit
    except (ValueError, OSError, KeyError, zipfile.BadZipFile, httpx.HTTPError) as exc:
        audit.update(state='failed', error=str(exc))
        raise ValueError(str(exc)) from exc
    finally:
        save(root / 'connector-runs' / (str(time.time_ns()) + '.json'), audit)
