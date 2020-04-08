import requests
from bs4 import BeautifulSoup as bs
import math
import csv
import threading
import multiprocessing
import time


# print(multiprocessing.cpu_count())


def get_divided_array(prod_links: [], threads: int):
    avg = len(prod_links) / float(threads)
    out = []
    last = 0.0

    while last < len(prod_links):
        out.append(prod_links[int(last):int(last + avg)])
        last += avg

    return out


class Scraper:

    @staticmethod
    def get_links_from_site(url: str):
        web = requests.get(url)
        webTxt = web.text
        soup = bs(webTxt, "html.parser")

        a_list = soup.find_all('a', class_='product-item-link')
        link_list = []

        for a in a_list:
            try:
                # print(a['href'])
                link_list.append(a['href'])
            except BaseException as e:
                pass

        return link_list

    @staticmethod
    def get_pages_amount(url: str):
        """
        :param url:
        :return: int - amount of pages
        """
        web = requests.get(url)
        webTxt = web.text
        soup = bs(webTxt, "html.parser")

        toolbar_amount = soup.find('p', {'id': 'toolbar-amount'}).find_all('span', class_='toolbar-number')
        products_amount = int(toolbar_amount[-1].text)

        pages = math.ceil(products_amount / 50)
        return pages

    @staticmethod
    def get_book_properties(product_url: str):
        web = requests.get(product_url)
        webTxt = web.text

        soup = bs(webTxt, "html.parser")
        product_info_attributes = soup.find('ul', class_='product-info-attributes')
        x = product_info_attributes.find_all('li')

        title = soup.find('span', attrs={'data-ui-id': 'page-title-wrapper', 'itemprop': 'name'}).text
        author = ''
        category = []
        cover = ''
        publisher = ''
        pages = ''
        release = ''

        price = soup.find('span', class_='price').text
        # price = soup.find('span', class_='price-wrapper').has_attr('data-price-amount').text

        for item in x:
            li = item
            span = item.span

            if 'autor' in str(span.text).lower():
                span.decompose()
                author = li.text.strip()

            if 'tegor' in str(span.text).lower():
                span.decompose()
                linkList = li.find_all('a')

                for cat in linkList:
                    category.append(cat.text)

            if 'typ okładki' in str(span.text).lower():
                span.decompose()
                cover = li.text.strip()

            if 'wydawca' in str(span.text).lower():
                span.decompose()
                publisher = li.text.strip()

            if 'ilość stron' in str(span.text).lower():
                span.decompose()
                pages = li.text.strip()

            if 'data wydania' in str(span.text).lower():
                span.decompose()
                release = li.text.strip()[0:10]

        # print(title)
        # print(author)
        # print(category)
        # print(cover)
        # print(publisher)
        # print(pages)
        # print(release)
        # print(price)

        return [title, author, category, cover, publisher, pages, release, price]

    def make_links_file(self, url: str):
        """
        Prepare csv file with all products urls which should be scraped.
        [important] Limit of product on url should be set as 50 otherwise some product could be skipped.
        :param url: Url of page where scraper should start its work
        :return: void
        """

        all_products_links = []

        pages_amount = self.get_pages_amount(url)

        for i in range(pages_amount):
            new_url = 'https://www.swiatksiazki.pl/Ksiazki/biznes-1765.html?p=%s&product_list_limit=50' % (i + 1)

            books_links = self.get_links_from_site(new_url)

            all_products_links.extend(books_links)

            i += 1

            if i > 2:
                break

        for link in all_products_links:
            with open('products_links.csv', 'a', newline='') as file:
                writter = csv.writer(file)
                writter.writerow([link])

    @staticmethod
    def get_links_from_file(file_name: str):
        links = []

        with open(file_name) as file:
            reader = csv.reader(file)

            for row in reader:
                links.extend(row)

            file.close()

        return links

    @staticmethod
    def save_book_properties_to_file(file_name: str, data):
        with open(file_name, 'a', encoding="utf-8", newline='') as file:
            writer = csv.writer(file, delimiter=',', )

            writer.writerow(data)

    def scrap(self, links: []):

        for link in links:
            book = self.get_book_properties(link)

            self.save_book_properties_to_file('products.csv', book)


def main():
    scraper_init = Scraper()

    links_list = scraper_init.get_links_from_file('products_links.csv')
    divided_list = get_divided_array(links_list, 4)

    scraper_1 = Scraper()
    scraper_2 = Scraper()
    scraper_3 = Scraper()
    scraper_4 = Scraper()

    thread_1 = threading.Thread(target=scraper_1.scrap, args={divided_list[0], })
    thread_2 = threading.Thread(target=scraper_2.scrap, args={divided_list[1], })
    thread_3 = threading.Thread(target=scraper_3.scrap, args={divided_list[2], })
    thread_4 = threading.Thread(target=scraper_4.scrap, args={divided_list[3], })

    thread_1.start()
    thread_2.start()
    thread_3.start()
    thread_4.start()


# run main
# main()