import re
import sys, asyncio, nest_asyncio
import time
from abc import ABC
from Project import Project

nest_asyncio.apply()


class Duproprio(Project, ABC):
    def __init__(self, pagination_mask):
        super().__init__(pagination_mask)

    # Ajout de méthodes spécifique pour le projet actuel

    def change_pagination(self, page_number):
        return self.pagination_mask.replace("{}", str(page_number))

    def extract_urls_from_page(self, page_number):
        """
        :return:
        """
        listing_page = self.change_pagination(page_number)
        elements = self.scrapper.find_elements(self.scrapper.get_page(listing_page, False), "div.search-results-listings > ul > li > a")
        return [list(item.absolute_links)[0] for item in elements] if elements else None

    def clean_string_isalnum(self, string):
        return "".join([character for character in string if character.isalnum()])

    def clean_string_isnum(self, string):
        return "".join([character for character in string if character.isnumeric()])

    def extract_floats_from_string(self, string):
        p = re.compile(r'\d+\.\d+')  # Compile a pattern to capture float values
        floats = [float(i) for i in p.findall(string)]  # Convert strings to float
        return floats

    def convert_dimensions_to_meter(self, value, unity=''):
        if unity == "acres":
            return float(value) / 0.00024711
        else:
            return float(value)

    def clean_dimensions(self, string: str):
        unities = [x for x in re.findall(r'[A-zÀ-ú]+', string) if not x.startswith('x')]
        numbers = re.findall(r'(?:\d+(?:\.\d*)?|\.\d+)(?:[, ](?:\d+(?:\.\d*)?|\.\d+))*', string)
        if 'x' in string:
            surface = round(float(numbers[2].replace(' ', '')) * float(numbers[3].replace(' ', '')), 2)
            return self.convert_dimensions_to_meter(surface, unities[1])
        else:
            output = float(numbers[1].replace(' ', '').replace(',', ''))
            return output if numbers else ''

    def process_elements(self, elements: dict):
        for k, v in elements.items():
            if k == "sold":
                elements[k] = 0 if v == "" else 1
            elif k == "price":
                result = re.findall(r'[-+]?\d*\.\d+|\d+', elements[k])
                elements[k] = float(result[0]) if result else ''
            elif k == "postal_code":
                s = self.clean_string_isalnum(elements[k])
                elements[k] = s if s != '' else ''
            elif k in ("living_space_area", "lot_dimensions") and v != '':
                elements[k] = self.clean_dimensions(elements[k])
            elif k in ('rooms', 'bathrooms', 'halfpaths'):
                elements[k] = int(elements[k]) if elements[k] != '' else elements[k]
            elif k == 'code':
                elements[k] = int(self.clean_string_isnum(elements[k]))
            elif k == 'type':
                elements[k] = elements[k].replace('à vendre', '')

        return elements

    async def start_scrapping(self, start_page_number, end_page_number):
        """
        :param end_page_number:
        :param start_page_number:
        :return:
        """
        if start_page_number > end_page_number:
            print("\033[31mLa page de fin et inférieure à la page de début!.\033[0m")
        number_page = start_page_number
        total_scrapped_data = 0
        tic = time.perf_counter()
        for i in range(start_page_number, end_page_number):
            # extract property urls from current listing page
            print("Collecte de la page de résultats numéro {}".format(number_page))
            print("=" * 50)
            current_property_urls = self.extract_urls_from_page(number_page)

            # For test purpose
            """
            current_property_urls.clear()
            current_property_urls.append("https://duproprio.com/fr/outaouais/gatineau/triplex-a-vendre/hab-triplex-171819")
            current_property_urls.append("https://duproprio.com/fr/monteregie-rive-sud-montreal/varennes/bungalow-a-vendre/hab-213-boul-de-la-marine-920126")
            """

            # Save extracted URLS to database
            self.save_urls(current_property_urls)

            # Get selectors
            selectors = self.get_selectors()

            # generate tasks for each property url
            tasks = self.scrapper.create_task_from_urls(current_property_urls)

            # fetch async from all current properties (11 for each page) in one shot
            responses = await self.scrapper.start_task(tasks)

            processed_data = []

            if responses:
                for r in responses:
                    # for each Response, scrap data
                    data = self.scrapper.get_elemets(r, selectors)

                    # Process data and add it to list
                    processed_data.append(self.process_elements(data))

                # Save scrapped data to database
                total_scrapped_data += self.save_scrapped_data(processed_data).rowcount

                # Increase listing page number
            number_page = number_page + 1

            # sleep for a random time
            self.scrapper.sleep()

        toc = time.perf_counter()
        print("Fin de la collecte")
        print(f"Durée de la collecte: {toc - tic:0.0f} secondes pour un total de {total_scrapped_data} urls")
