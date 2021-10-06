import asyncio
import random
import tldextract
from pyppeteer import launch
from lxml import html
from for_headers import REFERRER
import settings
from class_proxy import GetProxy
from class_header import Header


class RateUp(Header, GetProxy):

    def __init__(self):
        self.min_time = 15
        self.max_time = 30
        self.browser_path = r''
        self.good = 0
        self.bad = 0

    async def go_to_url(self, header, url, resolution, semaphore):
        width, height = resolution.split('×')

        ext = tldextract.extract(url)
        async with semaphore:
            try:
                proxy = self.get_proxy()
                # proxy = 1 #debug tat proxy
                contains_url = False
                if proxy:
                    self.good += 1
                    browser = await launch(
                        args=[
                            f'--window-size={width},{height}',
                            f'--proxy-server={proxy}',
                            '--disk-cache-size=0',
                            '--media-cache-size=0',
                            '--disable-application-cache',
                            '--no-sandbox'
                        ],
                        headless=False  # an hien trinh duyet
                    )
                    page = await browser.newPage()
                    await page.setViewport({'width': int(width), 'height': int(height)})
                    await page.setExtraHTTPHeaders(headers=header)
                    domain = url

                    try:
                        print(f'|==> New Visit: {domain} | {resolution} | {header}')
                        await page.goto(domain)
                        # treo o trinh duyet 3p.
                        await page.evaluate("""async () => {
                                        await new Promise((resolve, reject) => {
                                            var totalHeight = 0
                                            var distance = 100
                                            var timer = setInterval(() => {
                                                var scrollHeight = document.body.scrollHeight
                                                window.scrollBy(0, distance)
                                                totalHeight += distance
                                
                                                if(totalHeight >= scrollHeight){
                                                    clearInterval(timer)
                                                    resolve()
                                                }
                                            }, 1000)
                                        })
                                    }""")
                        await asyncio.sleep(random.uniform(self.min_time, self.max_time))
                    except Exception as e:
                        pages = await browser.pages()
                        for page in pages:
                            await page.close()
                        print(e)

                    for url in settings.LIST_URL:
                        try:
                            if url not in domain:
                                elements = await page.xpath(f"//a[contains(@href, '{url}')]")
                                for element in elements:
                                    try:
                                        contains_url = True
                                        print(f'|====> {proxy} Click to {url} | Ref: {domain}')
                                        await element.click()
                                        await asyncio.sleep(random.uniform(3, 5))
                                        pages = await browser.pages()
                                        new_page = pages[-1]
                                        await new_page.evaluate("""async () => {
                                        await new Promise((resolve, reject) => {
                                            var totalHeight = 0
                                            var distance = 100
                                            var timer = setInterval(() => {
                                                var scrollHeight = document.body.scrollHeight
                                                window.scrollBy(0, distance)
                                                totalHeight += distance
                                
                                                if(totalHeight >= scrollHeight){
                                                    clearInterval(timer)
                                                    resolve()
                                                }
                                            }, 1000)
                                        })
                                    }""")
                                        await asyncio.sleep(random.uniform(self.min_time, self.max_time))


                                        # els = await new_page.xpath(f"//div//a")
                                        # random_click = random.randrange(3)
                                        # for el in els[random_click: settings.NUMBER_OF_PAGE + random_click]:
                                        #     try:
                                        #         await el.click()
                                        #         await asyncio.sleep(random.uniform(3, 5))
                                        #     except Exception as e:
                                        #         print(e)
                                    except Exception as e:
                                        print(e)
                        except Exception as e:
                            print(e)
                            pages = await browser.pages()
                            for page in pages:
                                await page.close()
                    if not contains_url:
                        try:
                            list_urls = []
                            tree = html.fromstring(await page.content())
                            urls = tree.xpath('//a//@href')
                            for url in urls:
                                if url not in list_urls and 'facebook' not in url and 'linked' not in url and 'twitter' not in url:
                                    list_urls.append(url)
                            for i in range(settings.NUMBER_OF_PAGE):
                                try:
                                    url = random.choice(list_urls)
                                    list_urls.remove(url)
                                    await page.goto(url)
                                    await page.evaluate("""async () => {
                                        await new Promise((resolve, reject) => {
                                            var totalHeight = 0
                                            var distance = 100
                                            var timer = setInterval(() => {
                                                var scrollHeight = document.body.scrollHeight
                                                window.scrollBy(0, distance)
                                                totalHeight += distance
                                
                                                if(totalHeight >= scrollHeight){
                                                    clearInterval(timer)
                                                    resolve()
                                                }
                                            }, 1000)
                                        })
                                    }""")
                                    await asyncio.sleep(random.uniform(self.min_time, self.max_time))
                                except Exception as e:
                                    print(e)
                        except Exception as e:
                            pages = await browser.pages()
                            for page in pages:
                                await page.close()
                            print(e)
                    pages = await browser.pages()
                    for page in pages:
                        await page.close()
                else:
                    print('Proxy not work')
            except Exception as e:
                pages = await browser.pages()
                for page in pages:
                    await page.close()
                print(e)
                self.bad += 1

    async def main(self, header_list, url_list):
        # 20 tab chrome
        semaphore = asyncio.Semaphore(settings.NUM_PROCESS)
        queue = asyncio.Queue()
        task_list = []
        for url in url_list:
            resolution = random.choice(Header.screen_resolution)
            header = random.choice(header_list)
            task = asyncio.create_task(self.go_to_url(header, url, resolution, semaphore))
            task_list.append(task)
            await asyncio.sleep(0.5)

        await queue.join()
        await asyncio.gather(*task_list, return_exceptions=True)
        print(f'Good visits: {self.good}')
        print(f'Bad visits: {self.bad}')

    def start(self, header_list, site_url):
        asyncio.run(self.main(header_list, site_url))
