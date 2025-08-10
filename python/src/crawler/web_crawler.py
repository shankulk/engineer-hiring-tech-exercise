import asyncio
from urllib.parse import urlparse
import aiohttp
import tldextract
from bs4 import BeautifulSoup

from src.util.helpers import Helpers


class WebCrawler:
    def __init__(self, entered_url):
        self.base_url = entered_url.rstrip("/")
        parsed_url = urlparse(entered_url)
        extracted_url = tldextract.extract(parsed_url.netloc)
        self.base_domain = f'{extracted_url.domain}.{extracted_url.suffix}'
        self.base_scheme = parsed_url.scheme
        self.visited = set()
        self.queue = asyncio.Queue()
        self.session = None
        self.lock = asyncio.Lock()
        self.allowed_urls, self.disallowed_urls \
            = Helpers.parse_robots_txt(f"{self.base_scheme}://{self.base_domain}")

    def is_same_domain(self, url):
        parsed = urlparse(url)
        return parsed.scheme in ("http", "https") and parsed.netloc == self.base_domain


    async def fetch(self, url):
        try:
            async with self.session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                if resp.status == 200 and "text/html" in resp.headers.get("Content-Type", ""):
                    return await resp.text()
        except Exception:
            pass
        return None


    async def process_url(self):
        while True:
            try:
                url = await self.queue.get()
            except asyncio.CancelledError:
                return
            async with self.lock:
                if url in self.visited:
                    self.queue.task_done()
                elif url in self.disallowed_urls:
                    print(f"Skipping disallowed URL: {url}")
                    self.queue.task_done()
                    continue
                self.visited.add(url)
            html = await self.fetch(url)
            if html is None:
                self.queue.task_done()
                continue

            soup = BeautifulSoup(html, "html.parser")
            links = set()
            for a in soup.find_all("a", href=True):
                normalized = Helpers.normalize_url(a["href"], url)
                if self.is_same_domain(normalized):
                    print(f"Found link: {normalized}")
                    links.add(normalized)
            print(url)
            for l in links:
                print("  ", l)
            for l in links:
                async with self.lock:
                    if l not in self.visited:
                        self.queue.put_nowait(l)
            self.queue.task_done()


    async def crawl(self):
        async with aiohttp.ClientSession() as session:
            self.session = session
            await self.queue.put(self.base_url)
            workers = [
                # Adjust number of workers as needed (can be parameterised)
                asyncio.create_task(self.process_url()) for _ in range(10)
            ]
            await self.queue.join()
            for w in workers:
                w.cancel()
            await self.session.close()
