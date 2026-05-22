import asyncio
import aiohttp
import aiohttp_socks
import re
import os
import logging
from datetime import datetime, timedelta
from collections import defaultdict

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
log = logging.getLogger(__name__)

OUTPUT_DIR = "proxies"
os.makedirs(OUTPUT_DIR, exist_ok=True)

PROXY_TYPES = {
    "http": "proxies_http.txt",
    "https": "proxies_https.txt",
    "socks4": "proxies_socks4.txt",
    "socks5": "proxies_socks5.txt",
    "premium": "premium_type.txt",
}

for f in PROXY_TYPES.values():
    open(os.path.join(OUTPUT_DIR, f), "a").close()

SUMMARY_LOG = os.path.join(OUTPUT_DIR, "summary.log")

TEST_TIMEOUT = 5
CONCURRENCY = 500
MAX_PROXIES_PER_SOURCE = 5000

TEST_URLS = {
    "http": "http://httpbin.org/ip",
    "https": "https://httpbin.org/ip",
    "socks4": "http://httpbin.org/ip",
    "socks5": "http://httpbin.org/ip",
}

GITHUB_RAW_LISTS = {
    "http": [
        "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt",
        "https://raw.githubusercontent.com/ShiftyTR/Proxy-List/master/http.txt",
        "https://raw.githubusercontent.com/ShiftyTR/Proxy-List/master/https.txt",
        "https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/http.txt",
        "https://raw.githubusercontent.com/monosans/proxy-list/main/proxies_anonymous/http.txt",
        "https://raw.githubusercontent.com/Anonym0usWork1221/Free-Proxies/main/proxy_files/http.txt",
        "https://raw.githubusercontent.com/jetkai/proxy-list/main/online-proxies/txt/proxies-http.txt",
        "https://raw.githubusercontent.com/roosterkid/openproxylist/main/HTTP_RAW.txt",
        "https://raw.githubusercontent.com/TheSpeedX/SOCKS-Proxy/master/http.txt",
        "https://raw.githubusercontent.com/sunny9577/proxy-scraper/master/proxies.txt",
        "https://raw.githubusercontent.com/enseitankado/Proxy-List/main/HTTP.txt",
        "https://raw.githubusercontent.com/officialputixel/Proxy-List-EN/main/http.txt",
        "https://raw.githubusercontent.com/opengs/uab/master/data/proxy_ip_list/http.txt",
        "https://raw.githubusercontent.com/fahimscode/Proxy-List/master/http.txt",
        "https://raw.githubusercontent.com/themiralay/Proxy-List-World/master/http.txt",
        "https://raw.githubusercontent.com/mmpx12/proxy-list/master/http.txt",
        "https://raw.githubusercontent.com/vaken263/proxy-list/main/http.txt",
        "https://raw.githubusercontent.com/HyperBeast/proxy-list/master/http.txt",
        "https://raw.githubusercontent.com/B4RC0DE-TM/Proxy-List/main/http.txt",
    ],
    "https": [
        "https://raw.githubusercontent.com/ShiftyTR/Proxy-List/master/https.txt",
        "https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/http.txt",
        "https://raw.githubusercontent.com/jetkai/proxy-list/main/online-proxies/txt/proxies-http.txt",
        "https://raw.githubusercontent.com/opengs/uab/master/data/proxy_ip_list/http.txt",
        "https://raw.githubusercontent.com/officialputixel/Proxy-List-EN/main/http.txt",
    ],
    "socks4": [
        "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/socks4.txt",
        "https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/socks4.txt",
        "https://raw.githubusercontent.com/ShiftyTR/Proxy-List/master/socks4.txt",
        "https://raw.githubusercontent.com/Anonym0usWork1221/Free-Proxies/main/proxy_files/socks4.txt",
        "https://raw.githubusercontent.com/roosterkid/openproxylist/main/SOCKS4_RAW.txt",
        "https://raw.githubusercontent.com/jetkai/proxy-list/main/online-proxies/txt/proxies-socks4.txt",
        "https://raw.githubusercontent.com/enseitankado/Proxy-List/main/SOCKS4.txt",
        "https://raw.githubusercontent.com/officialputixel/Proxy-List-EN/main/socks4.txt",
        "https://raw.githubusercontent.com/fahimscode/Proxy-List/master/socks4.txt",
        "https://raw.githubusercontent.com/themiralay/Proxy-List-World/master/socks4.txt",
        "https://raw.githubusercontent.com/mmpx12/proxy-list/master/socks4.txt",
        "https://raw.githubusercontent.com/vaken263/proxy-list/main/socks4.txt",
        "https://raw.githubusercontent.com/HyperBeast/proxy-list/master/socks4.txt",
        "https://raw.githubusercontent.com/B4RC0DE-TM/Proxy-List/main/socks4.txt",
    ],
    "socks5": [
        "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/socks5.txt",
        "https://raw.githubusercontent.com/ShiftyTR/Proxy-List/master/socks5.txt",
        "https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/socks5.txt",
        "https://raw.githubusercontent.com/Anonym0usWork1221/Free-Proxies/main/proxy_files/socks5.txt",
        "https://raw.githubusercontent.com/hookzof/socks5_list/master/proxy.txt",
        "https://raw.githubusercontent.com/roosterkid/openproxylist/main/SOCKS5_RAW.txt",
        "https://raw.githubusercontent.com/jetkai/proxy-list/main/online-proxies/txt/proxies-socks5.txt",
        "https://raw.githubusercontent.com/sunny9577/proxy-scraper/master/proxies.txt",
        "https://raw.githubusercontent.com/enseitankado/Proxy-List/main/SOCKS5.txt",
        "https://raw.githubusercontent.com/officialputixel/Proxy-List-EN/main/socks5.txt",
        "https://raw.githubusercontent.com/fahimscode/Proxy-List/master/socks5.txt",
        "https://raw.githubusercontent.com/themiralay/Proxy-List-World/master/socks5.txt",
        "https://raw.githubusercontent.com/mmpx12/proxy-list/master/socks5.txt",
        "https://raw.githubusercontent.com/vaken263/proxy-list/main/socks5.txt",
        "https://raw.githubusercontent.com/HyperBeast/proxy-list/master/socks5.txt",
        "https://raw.githubusercontent.com/B4RC0DE-TM/Proxy-List/main/socks5.txt",
        "https://raw.githubusercontent.com/hanterm/proxy-list/master/socks5.txt",
    ],
}

GITHUB_ELITE_LISTS = {
    "http": [
        "https://raw.githubusercontent.com/monosans/proxy-list/main/proxies_anonymous/http.txt",
        "https://raw.githubusercontent.com/monosans/proxy-list/main/proxies_elite/http.txt",
    ],
    "socks4": [
        "https://raw.githubusercontent.com/monosans/proxy-list/main/proxies_anonymous/socks4.txt",
        "https://raw.githubusercontent.com/monosans/proxy-list/main/proxies_elite/socks4.txt",
    ],
    "socks5": [
        "https://raw.githubusercontent.com/monosans/proxy-list/main/proxies_anonymous/socks5.txt",
        "https://raw.githubusercontent.com/monosans/proxy-list/main/proxies_elite/socks5.txt",
    ],
}


def parse_proxy_line(line, default_type="http"):
    line = line.strip()
    if not line or line.startswith("#") or line.startswith("//"):
        return None

    parts = re.split(r"[\s:]+", line)
    ip_port = None

    if len(parts) >= 2 and re.match(r"\d+\.\d+\.\d+\.\d+", parts[0]):
        ip_port = f"{parts[0]}:{parts[1]}"
    else:
        match = re.search(r"(\d+\.\d+\.\d+\.\d+:\d+)", line)
        if match:
            ip_port = match.group(1)

    if not ip_port:
        return None

    ptype = default_type
    for t in ["socks5", "socks4", "https", "http"]:
        if t in line.lower():
            ptype = t
            break

    line_lower = line.lower()
    if any(p in line_lower for p in ["elite", "elite proxy", "high anonymity"]):
        anon = "elite"
    elif "anonymous" in line_lower:
        anon = "anonymous"
    elif "transparent" in line_lower:
        anon = "transparent"
    elif "distorting" in line_lower:
        anon = "distorting"
    else:
        anon = None

    return {"ip:port": ip_port, "type": ptype, "anonymity": anon}


def parse_html_table(html, default_type="http"):
    proxies = []
    rows = re.findall(r"<tr[^>]*>(.*?)</tr>", html, re.DOTALL | re.IGNORECASE)
    for row in rows:
        cells = re.findall(r"<t[dh][^>]*>(.*?)</t[dh]>", row, re.DOTALL | re.IGNORECASE)
        if len(cells) < 2:
            continue
        ip = re.sub(r"<[^>]+>", "", cells[0]).strip()
        port = re.sub(r"<[^>]+>", "", cells[1]).strip()
        if ip and port and re.match(r"\d+\.\d+\.\d+\.\d+", ip) and port.isdigit():
            anon_text = ""
            ptype = default_type
            for cell in cells[2:]:
                text = re.sub(r"<[^>]+>", "", cell).strip().lower()
                if text in ("elite", "anonymous", "transparent", "distorting"):
                    anon_text = text
                for t in ["socks5", "socks4", "https", "http"]:
                    if t in text:
                        ptype = t
            proxies.append({"ip:port": f"{ip}:{port}", "type": ptype, "anonymity": anon_text})
    return proxies


async def fetch_text(session, url, headers=None):
    try:
        kwargs = {"timeout": aiohttp.ClientTimeout(total=15)}
        if headers:
            kwargs["headers"] = headers
        async with session.get(url, **kwargs) as resp:
            if resp.status == 200:
                return await resp.text()
    except Exception:
        return None


async def fetch_json(session, url, headers=None):
    try:
        kwargs = {"timeout": aiohttp.ClientTimeout(total=15)}
        if headers:
            kwargs["headers"] = headers
        async with session.get(url, **kwargs) as resp:
            if resp.status == 200:
                return await resp.json()
    except Exception:
        return None


# ─── SOURCE SCRAPERS ───────────────────────────────────────────────

async def scrape_spys_me(session):
    log.info("Scraping spys.me...")
    proxies = []
    text = await fetch_text(session, "https://spys.me/proxy.txt")
    if not text:
        return proxies

    lines = text.split("\n")
    socks_idx = -1
    for i, line in enumerate(lines):
        if "socks" in line.lower():
            socks_idx = i
            break

    http_part = lines[5:socks_idx] if socks_idx != -1 else (lines[5:] if len(lines) > 5 else lines)
    for line in http_part:
        p = parse_proxy_line(line, "http")
        if p and p["ip:port"]:
            proxies.append(p)

    if socks_idx != -1:
        socks_part = lines[socks_idx:]
        mode = None
        for line in socks_part:
            if "socks4" in line.lower():
                mode = "socks4"
                continue
            elif "socks5" in line.lower():
                mode = "socks5"
                continue
            p = parse_proxy_line(line, mode or "socks5")
            if p and p["ip:port"]:
                p["type"] = mode or "socks5"
                if p["ip:port"] not in [x["ip:port"] for x in proxies]:
                    proxies.append(p)

    log.info(f"  spys.me: {len(proxies)} proxies")
    return proxies


async def scrape_proxyscrape(session, ptype):
    log.info(f"Scraping proxyscrape for {ptype}...")
    proxies = []
    for anon in ["elite", "anonymous", "transparent"]:
        url = f"https://api.proxyscrape.com/v2/?request=getproxies&protocol={ptype}&timeout=10000&country=all&ssl=all&anonymity={anon}"
        text = await fetch_text(session, url)
        if text:
            for line in text.split("\n"):
                line = line.strip()
                if line and ":" in line:
                    proxies.append({"ip:port": line, "type": ptype, "anonymity": anon})

    url2 = "https://api.proxyscrape.com/v3/free-proxy-list/get?request=displayproxies&proxy_format=protocolipport&format=text"
    text = await fetch_text(session, f"{url2}&protocol={ptype}")
    if text:
        for line in text.split("\n"):
            line = line.strip()
            if line and ":" in line:
                parts = line.split("://", 1)
                if len(parts) == 2:
                    proxies.append({"ip:port": parts[1], "type": ptype, "anonymity": None})
                else:
                    proxies.append({"ip:port": line, "type": ptype, "anonymity": None})

    log.info(f"  proxyscrape {ptype}: {len(proxies)} proxies")
    return proxies


async def scrape_geonode(session, ptype):
    log.info(f"Scraping geonode for {ptype}...")
    proxies = []
    mapped = {"http": "http", "https": "https", "socks4": "socks4", "socks5": "socks5"}
    url = f"https://proxylist.geonode.com/api/proxy-list?limit=500&page=1&sort_by=lastChecked&sort_type=desc&protocols={mapped.get(ptype, ptype)}"
    data = await fetch_json(session, url)
    if data and "data" in data:
        for entry in data["data"]:
            ip = entry.get("ip", "")
            port = entry.get("port", "")
            if ip and port:
                anon = entry.get("anonymityLevel", None)
                proxies.append({"ip:port": f"{ip}:{port}", "type": ptype, "anonymity": anon})
    log.info(f"  geonode {ptype}: {len(proxies)} proxies")
    return proxies


async def scrape_github_raw(session, ptype):
    log.info(f"Scraping GitHub raw lists for {ptype}...")
    proxies = []
    urls = GITHUB_RAW_LISTS.get(ptype, [])
    for url in urls:
        text = await fetch_text(session, url)
        if text:
            for line in text.split("\n"):
                line = line.strip()
                if ":" in line:
                    proxies.append({"ip:port": line, "type": ptype, "anonymity": None})
    log.info(f"  github-raw {ptype}: {len(proxies)} proxies")
    return proxies


async def scrape_github_elite(session, ptype):
    log.info(f"Scraping GitHub elite/anonymous lists for {ptype}...")
    proxies = []
    urls = GITHUB_ELITE_LISTS.get(ptype, [])
    for url in urls:
        text = await fetch_text(session, url)
        if text:
            for line in text.split("\n"):
                line = line.strip()
                if ":" in line:
                    proxies.append({"ip:port": line, "type": ptype, "anonymity": "elite" if "elite" in url else "anonymous"})
    log.info(f"  github-elite {ptype}: {len(proxies)} proxies")
    return proxies


async def scrape_html_table(session, url, default_type, label):
    log.info(f"Scraping {label}...")
    text = await fetch_text(session, url, headers={
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    })
    if not text:
        return []
    proxies = parse_html_table(text, default_type)
    log.info(f"  {label}: {len(proxies)} proxies")
    return proxies


async def scrape_free_proxy_list(session, ptype):
    if ptype == "http":
        return await scrape_html_table(session, "https://free-proxy-list.net/", "http", "free-proxy-list.net")
    return []


async def scrape_ssl_proxies(session, ptype):
    if ptype == "https":
        return await scrape_html_table(session, "https://www.sslproxies.org/", "https", "sslproxies.org")
    return []


async def scrape_us_proxies(session, ptype):
    if ptype == "http":
        return await scrape_html_table(session, "https://www.us-proxy.org/", "http", "us-proxy.org")
    return []


async def scrape_socks_proxy(session, ptype):
    if ptype in ("socks4", "socks5"):
        return await scrape_html_table(session, "https://www.socks-proxy.net/", "socks5", "socks-proxy.net")
    return []


async def scrape_proxynova(session, ptype):
    log.info(f"Scraping proxynova for {ptype}...")
    proxies = []
    url_map = {
        "http": "https://www.proxynova.com/proxy-server-list/",
        "https": "https://www.proxynova.com/proxy-server-list/",
        "socks4": "https://www.proxynova.com/proxy-server-list/socks4/",
        "socks5": "https://www.proxynova.com/proxy-server-list/socks5/",
    }
    url = url_map.get(ptype)
    if not url:
        return proxies

    text = await fetch_text(session, url, headers={
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Referer": "https://www.proxynova.com/",
    })
    if not text:
        return proxies

    rows = re.findall(r'<tr[^>]*>(.*?)</tr>', text, re.DOTALL)
    for row in rows:
        cells = re.findall(r'<td[^>]*>(.*?)</td>', row, re.DOTALL)
        if len(cells) < 2:
            continue
        ip_match = re.search(r'(\d+\.\d+\.\d+\.\d+)', cells[0])
        port_match = re.search(r'(\d+)', cells[1].replace('&nbsp;', '').strip())
        if ip_match and port_match:
            ip = ip_match.group(1)
            port = port_match.group(1)
            anon_text = ""
            if len(cells) > 4:
                anon_text = re.sub(r'<[^>]+>', '', cells[4]).strip().lower()
                if anon_text not in ("elite", "anonymous", "transparent", "distorting"):
                    anon_text = ""
            proxies.append({"ip:port": f"{ip}:{port}", "type": ptype, "anonymity": anon_text or None})

    log.info(f"  proxynova {ptype}: {len(proxies)} proxies")
    return proxies


async def scrape_openproxy(session, ptype):
    log.info(f"Scraping openproxy.space for {ptype}...")
    proxies = []
    mapped = {"http": "1", "https": "2", "socks4": "3", "socks5": "4"}
    pid = mapped.get(ptype)
    if not pid:
        return proxies
    url = f"https://openproxy.space/list/{pid}"
    data = await fetch_json(session, url)
    if not data:
        return proxies
    raw = data.get("data", "") if isinstance(data, dict) else data
    if isinstance(raw, str):
        for line in raw.strip().split("\n"):
            line = line.strip()
            if ":" in line:
                proxies.append({"ip:port": line, "type": ptype, "anonymity": None})
    elif isinstance(raw, list):
        for entry in raw:
            if isinstance(entry, str) and ":" in entry:
                proxies.append({"ip:port": entry, "type": ptype, "anonymity": None})
    log.info(f"  openproxy.space {ptype}: {len(proxies)} proxies")
    return proxies


async def scrape_proxylist_download(session, ptype):
    log.info(f"Scraping proxy-list.download for {ptype}...")
    proxies = []
    url = f"https://www.proxy-list.download/api/v1/get?type={ptype}"
    text = await fetch_text(session, url)
    if text:
        for line in text.split("\n"):
            line = line.strip()
            if ":" in line:
                proxies.append({"ip:port": line, "type": ptype, "anonymity": None})
    log.info(f"  proxy-list.download {ptype}: {len(proxies)} proxies")
    return proxies


async def scrape_hidemyname(session, ptype):
    log.info(f"Scraping hidemy.name for {ptype}...")
    proxies = []
    for page in range(1, 4):
        url = f"https://hidemy.name/en/proxy-list/?start={page * 64 - 64}#list"
        text = await fetch_text(session, url, headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        })
        if not text:
            continue
        rows = re.findall(r'<tr[^>]*>(.*?)</tr>', text, re.DOTALL)
        for row in rows:
            cells = re.findall(r'<td[^>]*>(.*?)</td>', row, re.DOTALL)
            if len(cells) < 6:
                continue
            ip = re.sub(r'<[^>]+>', '', cells[0]).strip()
            port = re.sub(r'<[^>]+>', '', cells[1]).strip()
            if ip and port and re.match(r'\d+\.\d+\.\d+\.\d+', ip) and port.isdigit():
                anon = re.sub(r'<[^>]+>', '', cells[5]).strip().lower()
                proxies.append({"ip:port": f"{ip}:{port}", "type": ptype, "anonymity": anon})
    log.info(f"  hidemy.name {ptype}: {len(proxies)} proxies")
    return proxies


async def scrape_aliveproxy(session, ptype):
    log.info(f"Scraping aliveproxy.com for {ptype}...")
    proxies = []
    url_map = {
        "http": "https://www.aliveproxy.com/proxy-list/",
        "https": "https://www.aliveproxy.com/https-proxy-list/",
        "socks4": "https://www.aliveproxy.com/socks4-proxy-list/",
        "socks5": "https://www.aliveproxy.com/socks5-proxy-list/",
    }
    url = url_map.get(ptype)
    if not url:
        return proxies

    text = await fetch_text(session, url, headers={
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    })
    if not text:
        return proxies

    rows = re.findall(r'<tr[^>]*>(.*?)</tr>', text, re.DOTALL)
    for row in rows:
        cells = re.findall(r'<td[^>]*>(.*?)</td>', row, re.DOTALL)
        if len(cells) < 2:
            continue
        ip = re.sub(r'<[^>]+>', '', cells[0]).strip()
        port = re.sub(r'<[^>]+>', '', cells[1]).strip()
        if ip and port and re.match(r'\d+\.\d+\.\d+\.\d+', ip) and port.isdigit():
            proxies.append({"ip:port": f"{ip}:{port}", "type": ptype, "anonymity": None})

    log.info(f"  aliveproxy {ptype}: {len(proxies)} proxies")
    return proxies


async def scrape_multiproxy(session, ptype):
    log.info(f"Scraping multiproxy.org for {ptype}...")
    proxies = []
    url = "https://multiproxy.org/txt_all/proxy.txt"
    text = await fetch_text(session, url)
    if text:
        for line in text.split("\n"):
            line = line.strip()
            if ":" in line:
                proxies.append({"ip:port": line, "type": ptype, "anonymity": None})
    log.info(f"  multiproxy.org: {len(proxies)} proxies")
    return proxies


async def scrape_proxybuff(session, ptype):
    log.info(f"Scraping proxybuff.com for {ptype}...")
    proxies = []
    url_map = {
        "http": "https://proxybuff.com/text/http.txt",
        "socks4": "https://proxybuff.com/text/socks4.txt",
        "socks5": "https://proxybuff.com/text/socks5.txt",
    }
    url = url_map.get(ptype)
    if not url:
        return proxies
    text = await fetch_text(session, url)
    if text:
        for line in text.split("\n"):
            line = line.strip()
            if ":" in line:
                proxies.append({"ip:port": line, "type": ptype, "anonymity": None})
    log.info(f"  proxybuff {ptype}: {len(proxies)} proxies")
    return proxies


async def scrape_proxylistme(session, ptype):
    log.info(f"Scraping proxylist.me for {ptype}...")
    proxies = []
    mapped = {"http": "http", "https": "https", "socks4": "socks4", "socks5": "socks5"}
    url = f"https://www.proxylist.me/api/proxy?protocol={mapped.get(ptype, ptype)}&limit=100&page=1"
    data = await fetch_json(session, url)
    if data and isinstance(data, list):
        for entry in data:
            ip = entry.get("ip", "")
            port = entry.get("port", "")
            if ip and port:
                proxies.append({"ip:port": f"{ip}:{port}", "type": ptype, "anonymity": None})
    log.info(f"  proxylist.me {ptype}: {len(proxies)} proxies")
    return proxies


async def scrape_proxypedia(session, ptype):
    log.info(f"Scraping proxypedia.org for {ptype}...")
    proxies = []
    url = f"https://proxypedia.org/{ptype}/"
    text = await fetch_text(session, url, headers={
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    })
    if not text:
        return proxies
    rows = re.findall(r'<tr[^>]*>(.*?)</tr>', text, re.DOTALL)
    for row in rows:
        cells = re.findall(r'<td[^>]*>(.*?)</td>', row, re.DOTALL)
        if len(cells) < 2:
            continue
        ip = re.sub(r'<[^>]+>', '', cells[0]).strip()
        port = re.sub(r'<[^>]+>', '', cells[1]).strip()
        if ip and port and re.match(r'\d+\.\d+\.\d+\.\d+', ip) and port.isdigit():
            anon = ""
            if len(cells) > 6:
                anon = re.sub(r'<[^>]+>', '', cells[6]).strip().lower()
            proxies.append({"ip:port": f"{ip}:{port}", "type": ptype, "anonymity": anon or None})
    log.info(f"  proxypedia {ptype}: {len(proxies)} proxies")
    return proxies


async def scrape_proxy11(session, ptype):
    log.info(f"Scraping proxy11.com for {ptype}...")
    proxies = []
    url = "https://proxy11.com/api/proxy?limit=100"
    data = await fetch_json(session, url, headers={
        "User-Agent": "Mozilla/5.0",
        "Referer": "https://proxy11.com/",
    })
    if data and isinstance(data, list):
        for entry in data:
            ip = entry.get("ip", "")
            port = entry.get("port", "")
            protocol = (entry.get("protocol", "") or "").lower()
            if ip and port:
                detected = ptype
                if "socks5" in protocol:
                    detected = "socks5"
                elif "socks4" in protocol:
                    detected = "socks4"
                elif "https" in protocol:
                    detected = "https"
                if detected == ptype:
                    proxies.append({"ip:port": f"{ip}:{port}", "type": ptype, "anonymity": None})
    log.info(f"  proxy11 {ptype}: {len(proxies)} proxies")
    return proxies


async def scrape_coolproxy(session, ptype):
    log.info(f"Scraping cool-proxy.net for {ptype}...")
    proxies = []
    url_map = {
        "http": "https://cool-proxy.net/proxies.json",
        "https": "https://cool-proxy.net/proxies_https.json",
        "socks4": "https://cool-proxy.net/proxies_socks4.json",
        "socks5": "https://cool-proxy.net/proxies_socks5.json",
    }
    url = url_map.get(ptype)
    if not url:
        return proxies
    data = await fetch_json(session, url)
    if data and isinstance(data, list):
        for entry in data:
            ip = entry.get("ip", "")
            port = entry.get("port", "")
            if ip and port:
                anon = entry.get("anonymity", None)
                if anon:
                    anon = anon.lower()
                proxies.append({"ip:port": f"{ip}:{port}", "type": ptype, "anonymity": anon})
    log.info(f"  cool-proxy {ptype}: {len(proxies)} proxies")
    return proxies


async def scrape_pubproxy(session, ptype):
    log.info(f"Scraping pubproxy.com for {ptype}...")
    proxies = []
    mapped = {"http": "http", "https": "https", "socks4": "socks4", "socks5": "socks5"}
    url = f"https://pubproxy.com/api/proxy?limit=20&format=json&type={mapped.get(ptype, ptype)}&country=all"
    data = await fetch_json(session, url, headers={
        "User-Agent": "Mozilla/5.0",
    })
    if data and "data" in data:
        for entry in data["data"]:
            ip = entry.get("ip", "")
            port = entry.get("port", "")
            if ip and port:
                proxies.append({"ip:port": f"{ip}:{port}", "type": ptype, "anonymity": None})
    log.info(f"  pubproxy {ptype}: {len(proxies)} proxies")
    return proxies


async def scrape_checkerproxy(session, ptype):
    log.info(f"Scraping checkerproxy.net for {ptype}...")
    proxies = []
    url = f"https://checkerproxy.net/api/archive/{datetime.now().strftime('%Y-%m-%d')}"
    data = await fetch_json(session, url)
    if data and isinstance(data, list):
        for entry in data:
            addr = entry.get("addr", "")
            kind = entry.get("kind", "").lower()
            if addr and ":" in addr:
                detected = ptype
                if "socks5" in kind:
                    detected = "socks5"
                elif "socks4" in kind:
                    detected = "socks4"
                elif "https" in kind:
                    detected = "https"
                if detected == ptype:
                    proxies.append({"ip:port": addr, "type": ptype, "anonymity": None})
    log.info(f"  checkerproxy {ptype}: {len(proxies)} proxies")
    return proxies


# ─── NEW ADDITIONAL SOURCES ────────────────────────────────────────

async def scrape_free_proxy_cz(session, ptype):
    log.info(f"Scraping free-proxy.cz for {ptype}...")
    proxies = []
    mapped = {"http": "http", "https": "https", "socks4": "socks4", "socks5": "socks5"}
    url = f"https://free-proxy.cz/en/proxylist/country/all/{mapped.get(ptype, ptype)}/ping/all"
    text = await fetch_text(session, url, headers={
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    })
    if not text:
        return proxies
    rows = re.findall(r'<tr[^>]*>(.*?)</tr>', text, re.DOTALL)
    for row in rows:
        cells = re.findall(r'<td[^>]*>(.*?)</td>', row, re.DOTALL)
        if len(cells) < 2:
            continue
        ip_match = re.search(r'(\d+\.\d+\.\d+\.\d+)', cells[0])
        port_match = re.search(r'(\d+)', cells[1])
        if ip_match and port_match:
            anon_text = ""
            if len(cells) > 4:
                anon_text = re.sub(r'<[^>]+>', '', cells[4]).strip().lower()
            proxies.append({"ip:port": f"{ip_match.group(1)}:{port_match.group(1)}", "type": ptype, "anonymity": anon_text or None})
    log.info(f"  free-proxy.cz {ptype}: {len(proxies)} proxies")
    return proxies


async def scrape_proxydb(session, ptype):
    log.info(f"Scraping proxydb.net for {ptype}...")
    proxies = []
    mapped = {"http": "http", "https": "https", "socks4": "socks4", "socks5": "socks5"}
    url = f"https://proxydb.net/?protocol={mapped.get(ptype, ptype)}&country=all"
    text = await fetch_text(session, url, headers={
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    })
    if not text:
        return proxies
    for match in re.finditer(r'(\d+\.\d+\.\d+\.\d+):(\d+)', text):
        ip, port = match.group(1), match.group(2)
        proxies.append({"ip:port": f"{ip}:{port}", "type": ptype, "anonymity": None})
    log.info(f"  proxydb {ptype}: {len(proxies)} proxies")
    return proxies


async def scrape_my_proxy(session, ptype):
    log.info(f"Scraping my-proxy.com for {ptype}...")
    proxies = []
    url_map = {
        "http": "https://www.my-proxy.com/free-proxy-list-1.html",
        "https": "https://www.my-proxy.com/free-elite-proxy-list-2.html",
        "socks4": "https://www.my-proxy.com/free-socks-4-proxy-list-4.html",
        "socks5": "https://www.my-proxy.com/free-socks-5-proxy-list-5.html",
    }
    url = url_map.get(ptype)
    if not url:
        return proxies
    text = await fetch_text(session, url, headers={
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    })
    if not text:
        return proxies
    for match in re.finditer(r'(\d+\.\d+\.\d+\.\d+)\s*#(\d+)', text):
        ip, port = match.group(1), match.group(2)
        proxies.append({"ip:port": f"{ip}:{port}", "type": ptype, "anonymity": None})
    log.info(f"  my-proxy.com {ptype}: {len(proxies)} proxies")
    return proxies


async def scrape_proxy_list_org(session, ptype):
    log.info(f"Scraping proxy-list.org for {ptype}...")
    proxies = []
    mapped = {"http": "http", "https": "https", "socks4": "socks4", "socks5": "socks5"}
    url = f"https://proxy-list.org/english/search.php?search=&country=all&type={mapped.get(ptype, ptype)}&port=&ssl=&anonymity="
    text = await fetch_text(session, url, headers={
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    })
    if not text:
        return proxies
    for match in re.finditer(r'(\d+\.\d+\.\d+\.\d+:\d+)', text):
        addr = match.group(1)
        proxies.append({"ip:port": addr, "type": ptype, "anonymity": None})
    log.info(f"  proxy-list.org {ptype}: {len(proxies)} proxies")
    return proxies


async def scrape_xroxy(session, ptype):
    log.info(f"Scraping xroxy.com for {ptype}...")
    proxies = []
    mapped = {"http": "0_0", "https": "0_0", "socks4": "0_4", "socks5": "0_5"}
    p = mapped.get(ptype, "0_0")
    url = f"https://www.xroxy.com/proxylist.php?port=&type%5B%5D={p}&ssl%5B%5D=&country=&latency=&reliability=&sort=reliability&desc=true"
    text = await fetch_text(session, url, headers={
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    })
    if not text:
        return proxies
    for row in re.findall(r'<tr[^>]*>(.*?)</tr>', text, re.DOTALL):
        cells = re.findall(r'<td[^>]*>(.*?)</td>', row, re.DOTALL)
        if len(cells) < 2:
            continue
        ip = re.sub(r'<[^>]+>', '', cells[0]).strip()
        port = re.sub(r'<[^>]+>', '', cells[1]).strip()
        if ip and port and re.match(r'\d+\.\d+\.\d+\.\d+', ip) and port.isdigit():
            proxies.append({"ip:port": f"{ip}:{port}", "type": ptype, "anonymity": None})
    log.info(f"  xroxy {ptype}: {len(proxies)} proxies")
    return proxies


async def scrape_proxywhale(session, ptype):
    log.info(f"Scraping proxywhale.com for {ptype}...")
    proxies = []
    mapped = {"http": "http", "https": "https", "socks4": "socks4", "socks5": "socks5"}
    url = f"https://proxywhale.com/api/proxies?protocol={mapped.get(ptype, ptype)}&limit=100&format=json"
    data = await fetch_json(session, url, headers={
        "User-Agent": "Mozilla/5.0",
    })
    if data and isinstance(data, list):
        for entry in data:
            ip = entry.get("ip", "") or entry.get("proxy", "")
            port = entry.get("port", "")
            if ip and port:
                proxies.append({"ip:port": f"{ip}:{port}", "type": ptype, "anonymity": None})
    elif data and isinstance(data, dict):
        items = data.get("data", []) or data.get("proxies", [])
        for entry in items:
            ip = entry.get("ip", "") or entry.get("proxy", "")
            port = entry.get("port", "")
            if ip and port:
                proxies.append({"ip:port": f"{ip}:{port}", "type": ptype, "anonymity": None})
    log.info(f"  proxywhale {ptype}: {len(proxies)} proxies")
    return proxies


async def scrape_best_proxies_ru(session, ptype):
    log.info(f"Scraping best-proxies.ru for {ptype}...")
    proxies = []
    url = "https://best-proxies.ru/free.txt"
    text = await fetch_text(session, url, headers={
        "User-Agent": "Mozilla/5.0",
    })
    if text:
        for line in text.split("\n"):
            line = line.strip()
            if ":" in line:
                p = parse_proxy_line(line, ptype)
                if p and p["ip:port"]:
                    proxies.append(p)
    log.info(f"  best-proxies.ru {ptype}: {len(proxies)} proxies")
    return proxies


async def scrape_proxy4free(session, ptype):
    log.info(f"Scraping proxy4free.com for {ptype}...")
    proxies = []
    url = "https://proxy4free.com/list/"
    text = await fetch_text(session, url, headers={
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    })
    if not text:
        return proxies
    rows = re.findall(r'<tr[^>]*>(.*?)</tr>', text, re.DOTALL)
    for row in rows:
        cells = re.findall(r'<t[dh][^>]*>(.*?)</t[dh]>', row, re.DOTALL)
        if len(cells) < 2:
            continue
        ip = re.sub(r'<[^>]+>', '', cells[0]).strip()
        port = re.sub(r'<[^>]+>', '', cells[1]).strip()
        if ip and port and re.match(r'\d+\.\d+\.\d+\.\d+', ip) and port.isdigit():
            detected_type = ptype
            for cell in cells:
                text = re.sub(r'<[^>]+>', '', cell).strip().lower()
                for t in ["socks5", "socks4", "https"]:
                    if t in text:
                        detected_type = t
            if detected_type == ptype:
                proxies.append({"ip:port": f"{ip}:{port}", "type": ptype, "anonymity": None})
    log.info(f"  proxy4free {ptype}: {len(proxies)} proxies")
    return proxies


async def scrape_proxifly(session, ptype):
    log.info(f"Scraping proxifly.com for {ptype}...")
    proxies = []
    mapped = {"http": "http", "https": "https", "socks4": "socks4", "socks5": "socks5"}
    url = f"https://proxifly.com/api/proxy-list?protocol={mapped.get(ptype, ptype)}&limit=100&format=json"
    data = await fetch_json(session, url, headers={
        "User-Agent": "Mozilla/5.0",
        "Referer": "https://proxifly.com/free-proxy-list/",
    })
    if data:
        items = []
        if isinstance(data, list):
            items = data
        elif isinstance(data, dict):
            items = data.get("data", []) or data.get("proxies", [])
        for entry in items:
            if isinstance(entry, str) and ":" in entry:
                proxies.append({"ip:port": entry, "type": ptype, "anonymity": None})
            elif isinstance(entry, dict):
                ip = entry.get("ip", "")
                port = entry.get("port", "")
                if ip and port:
                    proxies.append({"ip:port": f"{ip}:{port}", "type": ptype, "anonymity": None})
    log.info(f"  proxifly {ptype}: {len(proxies)} proxies")
    return proxies


async def scrape_sockslist(session, ptype):
    log.info(f"Scraping sockslist.net for {ptype}...")
    proxies = []
    url_map = {
        "socks4": "https://www.sockslist.net/list/socks4/",
        "socks5": "https://www.sockslist.net/list/socks5/",
    }
    url = url_map.get(ptype)
    if not url:
        return proxies
    text = await fetch_text(session, url, headers={
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    })
    if not text:
        return proxies
    for match in re.finditer(r'(\d+\.\d+\.\d+\.\d+):(\d+)', text):
        ip, port = match.group(1), match.group(2)
        proxies.append({"ip:port": f"{ip}:{port}", "type": ptype, "anonymity": None})
    log.info(f"  sockslist {ptype}: {len(proxies)} proxies")
    return proxies


# ─── PREMIUM / HIGH-ANON SPECIFIC SOURCES ──────────────────────────

async def scrape_premiumproxy_click(session, ptype):
    log.info(f"Scraping premiumproxy.click for {ptype}...")
    proxies = []
    mapped = {"http": "http", "https": "https", "socks4": "socks4", "socks5": "socks5"}
    url = f"https://premiumproxy.click/{mapped.get(ptype, ptype)}.txt"
    text = await fetch_text(session, url, headers={
        "User-Agent": "Mozilla/5.0",
    })
    if text:
        for line in text.split("\n"):
            line = line.strip()
            if ":" in line:
                proxies.append({"ip:port": line, "type": ptype, "anonymity": "elite"})
    log.info(f"  premiumproxy.click {ptype}: {len(proxies)} proxies")
    return proxies


async def scrape_highproxies(session, ptype):
    log.info(f"Scraping highproxies.com for {ptype}...")
    proxies = []
    url = "https://www.highproxies.com/"
    text = await fetch_text(session, url, headers={
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    })
    if not text:
        return proxies
    rows = re.findall(r'<tr[^>]*>(.*?)</tr>', text, re.DOTALL)
    for row in rows:
        cells = re.findall(r'<t[dh][^>]*>(.*?)</t[dh]>', row, re.DOTALL)
        if len(cells) < 2:
            continue
        ip = re.sub(r'<[^>]+>', '', cells[0]).strip()
        port = re.sub(r'<[^>]+>', '', cells[1]).strip()
        if ip and port and re.match(r'\d+\.\d+\.\d+\.\d+', ip) and port.isdigit():
            proxies.append({"ip:port": f"{ip}:{port}", "type": ptype, "anonymity": "elite"})
    log.info(f"  highproxies {ptype}: {len(proxies)} proxies")
    return proxies


async def scrape_elite_proxy(session, ptype):
    log.info(f"Scraping elite-proxy.com for {ptype}...")
    proxies = []
    url = "https://elite-proxy.com/"
    text = await fetch_text(session, url, headers={
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    })
    if not text:
        return proxies
    for match in re.finditer(r'(\d+\.\d+\.\d+\.\d+):(\d+)', text):
        ip, port = match.group(1), match.group(2)
        proxies.append({"ip:port": f"{ip}:{port}", "type": ptype, "anonymity": "elite"})
    log.info(f"  elite-proxy {ptype}: {len(proxies)} proxies")
    return proxies


async def scrape_free_proxy_list_net_elite(session, ptype):
    log.info(f"Scraping free-proxy-list.net elite for {ptype}...")
    proxies = []
    if ptype == "http":
        text = await fetch_text(session, "https://free-proxy-list.net/", headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        })
        if text:
            for p in parse_html_table(text, "http"):
                p["anonymity"] = "elite"
                proxies.append(p)
    log.info(f"  free-proxy-list.net elite {ptype}: {len(proxies)} proxies")
    return proxies


async def scrape_sslproxies_elite(session, ptype):
    log.info(f"Scraping sslproxies.org elite for {ptype}...")
    proxies = []
    if ptype == "https":
        text = await fetch_text(session, "https://www.sslproxies.org/", headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        })
        if text:
            for p in parse_html_table(text, "https"):
                p["anonymity"] = "elite"
                proxies.append(p)
    log.info(f"  sslproxies.org elite {ptype}: {len(proxies)} proxies")
    return proxies


async def scrape_anonymous_proxy_org(session, ptype):
    log.info(f"Scraping anonymous-proxy.org for {ptype}...")
    proxies = []
    url = "https://www.anonymous-proxy.org/"
    text = await fetch_text(session, url, headers={
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    })
    if not text:
        return proxies
    for match in re.finditer(r'(\d+\.\d+\.\d+\.\d+):(\d+)', text):
        ip, port = match.group(1), match.group(2)
        proxies.append({"ip:port": f"{ip}:{port}", "type": ptype, "anonymity": "anonymous"})
    log.info(f"  anonymous-proxy {ptype}: {len(proxies)} proxies")
    return proxies


async def scrape_ip_adress_proxy(session, ptype):
    log.info(f"Scraping ip-adress.com proxy list for {ptype}...")
    proxies = []
    url = "https://www.ip-adress.com/proxy-list"
    text = await fetch_text(session, url, headers={
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    })
    if not text:
        return proxies
    rows = re.findall(r'<tr[^>]*>(.*?)</tr>', text, re.DOTALL)
    for row in rows:
        cells = re.findall(r'<t[dh][^>]*>(.*?)</t[dh]>', row, re.DOTALL)
        if len(cells) < 2:
            continue
        ip = re.sub(r'<[^>]+>', '', cells[0]).strip()
        port = re.sub(r'<[^>]+>', '', cells[1]).strip()
        if ip and port and re.match(r'\d+\.\d+\.\d+\.\d+', ip) and port.isdigit():
            anon_text = ""
            if len(cells) > 4:
                anon_text = re.sub(r'<[^>]+>', '', cells[4]).strip().lower()
                if anon_text not in ("elite", "anonymous", "transparent", "distorting"):
                    anon_text = ""
            proxies.append({"ip:port": f"{ip}:{port}", "type": ptype, "anonymity": anon_text or None})
    log.info(f"  ip-adress proxy list {ptype}: {len(proxies)} proxies")
    return proxies


async def scrape_proxyserverlist24(session, ptype):
    log.info(f"Scraping proxyserverlist24 for {ptype}...")
    proxies = []
    url = "https://proxyserverlist-24.blogspot.com/"
    text = await fetch_text(session, url, headers={
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    })
    if not text:
        return proxies
    for match in re.finditer(r'(\d+\.\d+\.\d+\.\d+):(\d+)', text):
        ip, port = match.group(1), match.group(2)
        proxies.append({"ip:port": f"{ip}:{port}", "type": ptype, "anonymity": None})
    log.info(f"  proxyserverlist24 {ptype}: {len(proxies)} proxies")
    return proxies


# ─── TESTING ────────────────────────────────────────────────────────

async def test_proxy(session, proxy_info):
    ptype = proxy_info["type"]
    addr = proxy_info["ip:port"]

    if ptype in ("socks4", "socks5"):
        try:
            connector = aiohttp_socks.SocksConnector.from_url(f"{ptype}://{addr}")
            async with aiohttp.ClientSession(connector=connector) as socks_session:
                async with socks_session.get(
                    TEST_URLS[ptype], timeout=aiohttp.ClientTimeout(total=TEST_TIMEOUT)
                ) as resp:
                    if resp.status == 200:
                        return proxy_info
        except Exception:
            return None
    else:
        scheme = "https" if ptype == "https" else "http"
        proxy_url = f"{scheme}://{addr}"
        try:
            async with session.get(
                TEST_URLS[ptype],
                proxy=proxy_url,
                timeout=aiohttp.ClientTimeout(total=TEST_TIMEOUT),
            ) as resp:
                if resp.status == 200:
                    return proxy_info
        except Exception:
            return None

    return None


def is_premium(proxy_info):
    anon = (proxy_info.get("anonymity") or "").lower()
    return any(kw in anon for kw in ["elite", "anonymous", "high anonymity", "premium", "distorting"])


def save_proxies(proxies_by_type):
    for ptype, proxylist in proxies_by_type.items():
        if not proxylist:
            continue

        fname = PROXY_TYPES.get(ptype, f"proxies_{ptype}.txt")
        path = os.path.join(OUTPUT_DIR, fname)

        existing = set()
        if os.path.exists(path) and os.path.getsize(path) > 0:
            with open(path, "r") as f:
                for line in f:
                    line = line.strip()
                    if line:
                        existing.add(line)

        new_entries = [p["ip:port"] for p in proxylist if p["ip:port"] not in existing]
        if new_entries:
            with open(path, "a") as f:
                for entry in new_entries:
                    f.write(entry + "\n")
            log.info(f"Saved {len(new_entries)} new {ptype} proxies to {fname}")

    premium = [p for p in sum(proxies_by_type.values(), []) if is_premium(p)]
    if premium:
        path = os.path.join(OUTPUT_DIR, PROXY_TYPES["premium"])
        existing = set()
        if os.path.exists(path) and os.path.getsize(path) > 0:
            with open(path, "r") as f:
                for line in f:
                    parts = line.strip().split(" | ")
                    if parts:
                        existing.add(parts[0])

        with open(path, "a") as f:
            for p in premium:
                if p["ip:port"] not in existing:
                    f.write(f"{p['ip:port']} | type={p['type']} | anon={p.get('anonymity', 'unknown')}\n")
        log.info(f"Saved {len(premium)} premium proxies to premium_type.txt")


def write_summary(proxies_by_type, total_collected, total_after_dedup, working_count):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    lines = [
        f"Last updated: {now}",
        f"Total collected: {total_collected}",
        f"After dedup: {total_after_dedup}",
        f"Working proxies: {working_count}",
        "--- Working by type ---",
    ]
    for ptype in ["http", "https", "socks4", "socks5", "premium"]:
        count = len(proxies_by_type.get(ptype, []))
        fname = PROXY_TYPES.get(ptype, f"proxies_{ptype}.txt")
        lines.append(f"  {ptype}: {count} -> {fname}")
    premium = [p for ps in proxies_by_type.values() for p in ps if is_premium(p)]
    lines.append(f"  premium (elite/anonymous): {len(premium)} -> premium_type.txt")
    lines.append("")
    with open(SUMMARY_LOG, "w") as f:
        f.write("\n".join(lines))


# ─── ORCHESTRATION ──────────────────────────────────────────────────

SOURCES_WITH_PTYPE = {
    "proxyscrape": scrape_proxyscrape,
    "geonode": scrape_geonode,
    "github-raw": scrape_github_raw,
    "github-elite": scrape_github_elite,
    "openproxy.space": scrape_openproxy,
    "proxy-list.download": scrape_proxylist_download,
    "proxynova.com": scrape_proxynova,
    "aliveproxy": scrape_aliveproxy,
    "proxybuff": scrape_proxybuff,
    "proxylist.me": scrape_proxylistme,
    "proxypedia": scrape_proxypedia,
    "proxy11": scrape_proxy11,
    "cool-proxy": scrape_coolproxy,
    "pubproxy": scrape_pubproxy,
    "checkerproxy": scrape_checkerproxy,
    "free-proxy.cz": scrape_free_proxy_cz,
    "proxydb": scrape_proxydb,
    "my-proxy": scrape_my_proxy,
    "proxy-list.org": scrape_proxy_list_org,
    "xroxy": scrape_xroxy,
    "proxywhale": scrape_proxywhale,
    "best-proxies.ru": scrape_best_proxies_ru,
    "proxy4free": scrape_proxy4free,
    "proxifly": scrape_proxifly,
    "sockslist": scrape_sockslist,
    "premiumproxy.click": scrape_premiumproxy_click,
    "highproxies": scrape_highproxies,
    "elite-proxy": scrape_elite_proxy,
    "sslproxies-elite": scrape_sslproxies_elite,
    "free-proxy-list-elite": scrape_free_proxy_list_net_elite,
    "anonymous-proxy.org": scrape_anonymous_proxy_org,
    "ip-adress.com": scrape_ip_adress_proxy,
    "proxyserverlist24": scrape_proxyserverlist24,
}


async def run_cycle():
    log.info("=" * 60)
    log.info("Starting proxy scraping cycle")
    log.info("=" * 60)

    connector = aiohttp.TCPConnector(
        limit=CONCURRENCY, limit_per_host=5, force_close=True, ttl_dns_cache=300
    )
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
    }
    async with aiohttp.ClientSession(connector=connector, headers=headers) as session:
        all_proxies = []

        # HTML table scrapers (one type each)
        for ptype in ["http", "https", "socks4", "socks5"]:
            all_proxies.extend(await scrape_free_proxy_list(session, ptype))
            all_proxies.extend(await scrape_ssl_proxies(session, ptype))
            all_proxies.extend(await scrape_us_proxies(session, ptype))
            all_proxies.extend(await scrape_socks_proxy(session, ptype))

        # Single-source scrapers
        all_proxies.extend(await scrape_spys_me(session))
        all_proxies.extend(await scrape_hidemyname(session, "http"))
        all_proxies.extend(await scrape_multiproxy(session, "http"))

        # Multi-type scrapers
        for ptype in ["http", "https", "socks4", "socks5"]:
            for name, scraper_fn in SOURCES_WITH_PTYPE.items():
                result = await scraper_fn(session, ptype)
                if len(result) > MAX_PROXIES_PER_SOURCE:
                    log.info(f"  trimming {name} {ptype} from {len(result)} to {MAX_PROXIES_PER_SOURCE}")
                    result = result[:MAX_PROXIES_PER_SOURCE]
                all_proxies.extend(result)

        log.info(f"Total proxies collected: {len(all_proxies)}")

        # Deduplicate by (ip:port, type)
        seen = set()
        deduped = []
        for p in all_proxies:
            key = (p["ip:port"], p["type"])
            if key not in seen:
                seen.add(key)
                deduped.append(p)
        log.info(f"After dedup: {len(deduped)} proxies")

        log.info("Testing proxies for connectivity...")
        sem = asyncio.Semaphore(CONCURRENCY)
        tested = 0
        total_to_test = len(deduped)

        async def test_with_sem(p):
            nonlocal tested
            async with sem:
                result = await test_proxy(session, p)
                tested += 1
                if tested % 1000 == 0:
                    log.info(f"  tested {tested}/{total_to_test} proxies...")
                return result

        tasks = [test_with_sem(p) for p in deduped]
        results = await asyncio.gather(*tasks)

        working = [r for r in results if r is not None]
        log.info(f"Working proxies: {len(working)}/{total_to_test}")

        proxies_by_type = defaultdict(list)
        for p in working:
            proxies_by_type[p["type"]].append(p)

        log.info(f"Working by type: { {k: len(v) for k, v in proxies_by_type.items()} }")
        save_proxies(proxies_by_type)
        write_summary(proxies_by_type, len(all_proxies), len(deduped), len(working))


async def main():
    log.info("Proxy Scraper started - running 24/7")
    log.info(f"Output directory: {os.path.abspath(OUTPUT_DIR)}")
    log.info("Cycle interval: every 10 minutes")

    while True:
        try:
            await run_cycle()
        except Exception as e:
            log.error(f"Cycle failed: {e}", exc_info=True)

        log.info(f"Sleeping 10m until next cycle at {(datetime.now() + timedelta(minutes=10)).strftime('%H:%M:%S')}")
        await asyncio.sleep(600)


if __name__ == "__main__":
    asyncio.run(main())
