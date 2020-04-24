import requests
from bs4 import BeautifulSoup as bs
import math
import csv
import time
import threading
import os
from random import randrange
from program import datasets, utils


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
    random = randrange(1, 13)

    if random in [8, 9]:
        time.sleep(2)
    elif random == 10:
        time.sleep(4)
    else:
        return


class Scraper:
    category_main_page_url = None
    category_scrap_url = None
    category_name = None
    gui = None
    thread_scrap_books = None

    def __init__(self, category: str, gui):
        try:
            self.category_name = category
            self.category_main_page_url = datasets.categories[category]['main_url']
            self.category_scrap_url = self.category_main_page_url + '?p=%s&product_list_limit=50'
            self.gui = gui
            self.thread_scrap_books = threading.Thread(target=self.scrap_books, name='thread_scrap_books')

        except BaseException as error:
            utils.log_to_file('Scraper init -> ' + str(error))
            utils.send_log_email()
            gui.push_log_status(datasets.notifications['scraper_crashed'])

    def get_products_amount(self):
        """
        Return amount of product from category based on info scraped from main category site
        :return: Integer
        """
        soup = get_page_soup(self.category_main_page_url)

        toolbar_amount = soup.find('p', {'id': 'toolbar-amount'}).find_all('span', class_='toolbar-number')
        products_amount = int(toolbar_amount[-1].text)

        self.gui.push_log_status(
            datasets.notifications['amount_of_products'] % (self.category_name, str(products_amount)))

        print('---------get_products_amount: ' + str(products_amount))
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
                link_list.append(a['href'])
            except BaseException as e:
                pass

        print('---------get_links_from_site: ' + str(len(link_list)))
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

        print('---------get_pages_amount: ' + str(pages))
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
        category = ''
        cover = ''
        publisher = ''
        pages = ''
        release = ''

        price = soup.find('span', class_='price').text
        price = price.replace('\xa0zł', '').replace(',', '.')

        for item in x:
            li = item
            span = item.span

            if 'autor' in str(span.text).lower():
                span.decompose()
                author = li.text.strip()

            if 'kategorie' in str(span.text).lower():
                span.decompose()
                linkList = li.find_all('a')

                for cat in linkList:
                    category += (cat.text + "; ")

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

        # print(title, author, category, cover,
        #       publisher, pages, release, price)

        return [title, author, category, cover,
                publisher, pages, release, price]

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
        with open(self.category_name + '_books.csv', 'a', newline='', encoding='utf-8') as file:
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
            self.gui.push_log_status(datasets.notifications['links_file_deleted'] % (self.category_name))
            os.remove(self.category_name + '_links.csv')

        all_products_links = []

        pages_amount = self.get_pages_amount()

        for i in range(pages_amount):
            new_url = self.category_scrap_url % (i + 1)

            books_links = self.get_links_from_site(new_url)

            all_products_links.extend(books_links)

            i += 1

        for link in all_products_links:
            with open(self.category_name + '_links.csv', 'a', newline='') as file:
                writer = csv.writer(file)
                writer.writerow([link])

        self.gui.push_log_status(datasets.notifications['links_file_created'])

    def scrap_books(self):
        """
        (Run scraping process)
        Get list of links and call scraper's method for all of them, next save scraped data to file
        :return: void
        """
        self.gui.push_log_status(datasets.notifications['scraper_work_prepare'])

        # Disable 'rub button' to prevent rerun scraper thread
        self.gui.run_btn['state'] = 'disabled'

        # Remove old books-data file if exist
        if os.path.isfile(self.category_name + '_books.csv'):
            self.gui.push_log_status(datasets.notifications['books_file_deleted'] % (self.category_name))
            os.remove(self.category_name + '_books.csv')

        list_of_links = self.get_links_from_file()

        counter = 0
        self.gui.push_log_status(datasets.notifications['books_file_added'] % (self.category_name))
        for link in list_of_links:
            book_data = self.get_book_properties(link)
            self.save_book_properties_to_file(book_data)

            counter += 1
            if counter % 20 == 0:
                self.gui.push_log_status(
                    datasets.notifications['scraped_amount_notification'] % (str(counter), str(len(list_of_links))))

            make_random_pause()

        utils.log_to_file('Scraping finished')
        utils.send_log_email()

        if self.gui.turn_comp_off.get():
            self.gui.push_log_status(datasets.notifications['scraper_work_finished_off'])
            utils.turn_computer_off()
        else:
            self.gui.push_log_status(datasets.notifications['scraper_work_finished'])

    def main(self):
        """
        Main Scraper function that prepare environment and run scraper process
        :return:
        """

        self.gui.push_log_status(datasets.notifications['scraper_work_prepare'])
        if self.links_file_exist():
            amount_of_product_in_store = self.get_products_amount()

            if self.links_file_is_complete(amount_of_product_in_store):

                self.thread_scrap_books.start()
            else:
                self.make_links_file()

                self.thread_scrap_books.start()
        else:
            self.make_links_file()

            self.thread_scrap_books.start()


def run_scraper(category: str, gui):
    scraper = Scraper(category, gui)
    scraper.main()
