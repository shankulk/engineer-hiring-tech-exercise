import asyncio
import sys

from src.crawler import web_crawler


async def main():
    while True:
        entered_url = input('Enter a url to start crawling: ')
        if not entered_url.startswith(('http://', 'https://')):
            print('Please enter a valid URL starting with http:// or https://')
        else:
            break

    crawler = web_crawler.WebCrawler(entered_url)
    try:
        await crawler.crawl()
    except KeyboardInterrupt:
        print('Stopped crawling.')
        sys.exit(0)


if __name__ == "__main__":
    asyncio.run(main())
