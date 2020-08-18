import datetime
import random
import re
import time
import requests
from requests_html import AsyncHTMLSession, HTMLSession

# Important : Do not delete those imports
import pyppeteer
import pyppdf.patch_pyppeteer


class AsyncCollector:
    def __init__(self):
        self.session = AsyncHTMLSession()

    def get_status(self, response):
        return True if response.status_code in range(200, 300) else False

    def remove_quotes(self, string):
        s = string.strip()
        if s.startswith('"') and s.strip().endswith('"'):
            s = s[1:-1]
        return s.replace('""', '\"')

    def search_element(self, response, mask):
        s = mask.strip()
        if '""' in mask:
            s = mask.replace('""', '\"')
        r = response.html.search(mask)
        return r[0] if r is not None else None

    def find_element(self, response, selector):
        return response.html.find(selector)[0].text if response.html.find(selector) else ""

    def get_elemets(self, response, selectors: dict, mask="{}"):
        output = {}
        for k, v in selectors.items():
            if mask in v:
                output[k] = re.sub(r'[^ ,\'\nA-Za-z0-9À-ÖØ-öø-ÿ/-]+', '', self.search_element(response, v))
            else:
                output[k] = re.sub(r'[^ ,\'\nA-Za-z0-9À-ÖØ-öø-ÿ/-]+', '', self.find_element(response, v))

            output['fk_link'] = response.url
            output['created'] = str(datetime.datetime.now())
        return output

    def find_elements(self, response, selector):
        return response.html.find(selector) if response else None

    def create_task_from_urls(self, urls):
        """
        :param urls:
        :return: List of functions
        """
        return [lambda url=url: self.get_page_async(url, False) for url in urls] if urls else None

    async def start_task(self, tasks_list):
        """
        :param tasks_list:
        :return: list of responses
        """
        results = self.session.run(*tasks_list) if tasks_list else None
        # await self.session.close()

        # [await result.html.arender() for result in results]

        return results

    def get_page(self, page_url, need_render=True):
        r = None
        try:
            asession = HTMLSession()
            r = asession.get(page_url)
            if need_render:
                r.html.render()

            asession.close()
            return r
        except requests.exceptions.ConnectionError as e:
            print("\033[31mImpossible de se connecter au site.\033[0m")

    async def get_page_async(self, page_url, need_render=True):

        self.sleep(0.3)
        asession = AsyncHTMLSession()
        r = await asession.get(page_url)
        print(f"Connexion à {page_url}...")
        self.sleep(0.3)
        await asession.close()
        # print(f"Connecté")
        return r

    def sleep(self, fixed: float = None):
        delay = random.randint(2, 4)
        time.sleep(delay) if fixed is None else time.sleep(fixed)

