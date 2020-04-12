import requests
from bs4 import BeautifulSoup as bs
import math
import csv
import multiprocessing
import time
import threading
import os
from random import randrange
from datasets import categories


def get_divided_array(prod_links: [], threads: int):
    avg = len(prod_links) / float(threads)
    out = []
    last = 0.0

    while last < len(prod_links):
        out.append(prod_links[int(last):int(last + avg)])
        last += avg

    return out


def get_page_soup(url: str):
    """
    Return BeautifulSoup object of web page
    :param url:
    :return:
    """
    page = requests.get(url)
    page_txt = page.text
    soup = bs(page_txt, "html.parser")

    return soup


def make_random_pause():
    random = randrange(1, 11)

    if random in [6, 7]:
        time.sleep(1)
    elif random in [8, 9]:
        time.sleep(2)
    elif random == 10:
        time.sleep(6)
    else:
        return


class Scraper:
    category_main_page_url = None
    category_scrap_url = None
    category_name = None

    def __init__(self, category: str):
        self.category_name = category
        self.category_main_page_url = categories[category]['main_url']
        self.category_scrap_url = categories[category]['scrap_url']

    def get_products_amount(self):
        """
        Return amount of product from category based on info scraped from main category site
        :return: Integer
        """
        soup = get_page_soup(self.category_main_page_url)

        toolbar_amount = soup.find('p', {'id': 'toolbar-amount'}).find_all('span', class_='toolbar-number')
        products_amount = int(toolbar_amount[-1].text)

        return products_amount

    def links_file_exist(self):
        """
        Check if file with links to scrap exist
        :return: Boolean
        """
        if os.path.isfile(self.category_name + "_links.csv"):
            return True
        else:
            return False

    def links_file_is_complete(self, products_amount: int):
        """
        Check if file contains 60% or more links of all products from category
        :param products_amount: Integer
        :return: Boolean
        """
        with open(self.category_name + "_links.csv", "r") as links_file:
            reader = csv.reader(links_file)

            amount_in_file = len(list(reader))

            links_file.close()

            return True if int(amount_in_file) / products_amount >= 0.6 else False

    @staticmethod
    def get_links_from_site(url: str):
        """
        Return list of products urls from current subsite
        :param url: String
        :return: List of Stings
        """
        soup = get_page_soup(url)

        a_list = soup.find_all('a', class_='product-item-link')
        link_list = []

        for a in a_list:
            try:
                # print(a['href'])
                link_list.append(a['href'])
            except BaseException as e:
                pass

        return link_list

    def get_pages_amount(self):
        """
        Return amount of all pages from selected category if 50 products are shown on site
        :return: Integer
        """
        soup = get_page_soup(self.category_main_page_url)

        toolbar_amount = soup.find('p', {'id': 'toolbar-amount'}).find_all('span', class_='toolbar-number')
        products_amount = int(toolbar_amount[-1].text)

        pages = math.ceil(products_amount / 50)
        return int(pages)

    @staticmethod
    def get_book_properties(product_url: str):
        """
        Return dictionary of book properties
        :param product_url: String
        :return: List -> [title, author, category, cover, publisher, pages, release, price]
        """
        soup = get_page_soup(product_url)
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
        # return {'title': title, 'author': author,
        #         'category': category, 'publisher': publisher,
        #         'pages': pages, 'release': release,
        #         'price': price, 'cover': cover}

    def get_links_from_file(self):
        """
        Return list of links from links-file
        :return: List of Stings
        """
        links = []

        with open(self.category_name + "_links.csv") as file:
            reader = csv.reader(file)

            for row in reader:
                links.extend(row)

            file.close()

        return links

    def save_book_properties_to_file(self, data):
        """
        Save received book data to file
        :param data:
        :return: void
        """
        with open(self.category_name + '_books.csv', 'a', encoding="utf-8", newline='') as file:
            writer = csv.writer(file, delimiter=',')

            writer.writerow(data)

    def make_links_file(self):
        """
        Prepare csv file with all products urls which should be scraped.
        [important] Limit of product on url should be set as 50 otherwise some product could be skipped.
        :return: void
        """

        # check if empty or incomplete fie exist and remove it ( to create new one )
        if self.links_file_exist():
            os.remove(self.category_name + '_links.csv')

        all_products_links = []

        pages_amount = self.get_pages_amount()

        for i in range(pages_amount):
            new_url = self.category_scrap_url % (i + 1)

            books_links = self.get_links_from_site(new_url)

            all_products_links.extend(books_links)

            i += 1

            # todo:: remove test break
            if i > 2:
                break

        for link in all_products_links:
            with open(self.category_name + '_links.csv', 'a', newline='') as file:
                writer = csv.writer(file)
                writer.writerow([link])

    def scrap_books(self):
        """
        (Run scraping process)
        Get list of links and call scraper's method for all of them, next save scraped data to file
        :return: void
        """

        # Remove old books-data file if exist
        if os.path.isfile(self.category_name + '_books.csv'):
            os.remove(self.category_name + '_books.csv')

        list_of_links = self.get_links_from_file()

        for link in list_of_links:
            book_data = self.get_book_properties(link)
            self.save_book_properties_to_file(book_data)
            make_random_pause()

    def run_scraper(self):
        """
        Main Scraper function that prepare environment and run scraper process
        :return:
        """
        if self.links_file_exist():
            amount_of_product_in_store = self.get_products_amount()

            if self.links_file_is_complete(amount_of_product_in_store):
                self.scrap_books()
            else:
                self.make_links_file()
                self.scrap_books()
        else:
            self.make_links_file()
            self.scrap_books()


# main


