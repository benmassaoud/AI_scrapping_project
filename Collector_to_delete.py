from requests_html import HTMLSession, AsyncHTMLSession


class Collector:
    def __init__(self, url):
        self.url = url
        self.session = HTMLSession()
        self.async_session = AsyncHTMLSession()
        self.content = self.get_page_content()
        self.status = self.content.status_code

    def __del__(self):
        self.session.close()

    def get_status(self):
        return True if self.status in range(200, 300) else False

    def get_page_content(self):
        response = self.session.get(self.url)
        response.html.render()
        return response

    def search_element(self, mask):
        response = self.content.html.search(mask)
        return response[0] if response is not None else None

    def find_element(self, selector):
        return self.content.html.find(selector)[0].text

    def find_elements(self, selector):
        return self.content.html.find(selector)

    def get_elemets(self, selectors: dict):
        output = {}
        for k, v in selectors.items():
            if "{}" in v:
                output[k] = self.search_element(v).encode("ascii", "ignore").decode()
            else:
                output[k] = self.find_element(v).encode("ascii", "ignore").decode()
        return output


"""
session = HTMLSession()
resp = session.get(startUrlListing)
resp.html.render()
last_page = resp.html.find("#react-component-SearchPagination > nav > ul > li:last-child > a")[0].text

# PostalCode of property
propertyUrl = "https://duproprio.com/fr/lanaudiere/terrebonne-la-plaine/maison-a-vendre/hab-1270-rue-de-labricotier-910144#description"
resp_prop = session.get(propertyUrl)
resp_prop.html.render()
postalCode = resp_prop.html.search('"postalCode": "{}"')[0]
print(last_page, postalCode)
"""
