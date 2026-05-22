# beta-01

Initial release of the multi-source proxy scraper.

## Features
- **40+ proxy sources** including GitHub raw lists, proxyscrape, geonode, spys.me, and more
- **All proxy types**: HTTP, HTTPS, SOCKS4, SOCKS5
- **Live connectivity testing** before saving
- **Premium/elite/anonymous detection** saved to `premium_type.txt`
- **Deduplication** across all sources per cycle
- **24/7 operation** with configurable cycle interval (default: 10 min)
- **Rewritable summary log** (`proxies/summary.log`)

## Usage
```bash
pip install -r requirements.txt
python proxy_scraper.py
```
