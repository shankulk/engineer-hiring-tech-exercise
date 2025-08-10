from urllib.parse import urlparse, urljoin
import requests

class Helpers:

    @staticmethod
    def parse_robots_txt(url):
        robots_url = url.rstrip('/') + '/robots.txt'
        response = requests.get(robots_url, timeout=30)
        allow = []
        disallow = []
        for line in response.text.splitlines():
            line = line.strip()
            if line.startswith('Allow:'):
                path = line[len('Allow:'):].strip()
                allow.append(path)
            elif line.startswith('Disallow:'):
                path = line[len('Disallow:'):].strip()
                disallow.append(path)
        return allow, disallow


    @staticmethod
    def normalize_url(url, current_url):
        # Remove fragments, resolve relative URLs, etc.
        joined = urljoin(current_url, url)
        parsed = urlparse(joined)
        norm_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
        if parsed.query:
            norm_url += f"?{parsed.query}"
        return norm_url

if __name__ == "__main__":
    allowed_urls, disallowed_urls = Helpers.parse_robots_txt("https://google.com")
    print(f'allowed_urls: {allowed_urls}')
    print(f'disallowed_urls: {disallowed_urls}')
