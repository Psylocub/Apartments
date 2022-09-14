from datetime import datetime, timedelta

from peewee import PostgresqlDatabase, Model, CharField, TextField, DateField
from selenium import webdriver
from selenium.common import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

db = PostgresqlDatabase(database='apartments', user='postgres', password='123', host='localhost')


class Apartments(Model):
    image = TextField()
    title = CharField()
    location = CharField()
    date = DateField()
    bedrooms = CharField()
    description = TextField()
    price = CharField()
    currency = CharField()

    class Meta:
        database = db


def main():
    """Placing list of dicts with apartments data in database"""
    db.connect()
    db.create_tables([Apartments])
    # selenium settings:
    apartments_information_list = []
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    for page in range(1, 95):
        driver.get(f"https://www.kijiji.ca/b-apartments-condos/city-of-toronto/page-{page}/c37l1700273")
        website_ads = driver.find_elements(By.CLASS_NAME, "clearfix")
        for ad in website_ads:
            if ad.get_attribute('class') != 'layout-0 breadcrumbLayout clearfix':
                apartments_information_list.append(rendering_page(ad))
    driver.quit()
    # push data from list of dict to database:
    with db.atomic():
        for row in apartments_information_list:
            Apartments.create(**row)
    db.close()


def rendering_page(ad):
    """Rendering page and place apartments data in dict"""

    try:
        image = ad.find_element(By.TAG_NAME, "source").get_attribute("srcset")
    except NoSuchElementException:
        image = ""
    title = ad.find_element(By.CLASS_NAME, "title").text
    crude_date = ad.find_element(By.CLASS_NAME, "date-posted").text
    if "/" in crude_date:
        date = crude_date.replace('/', '-')
    else:
        yesterday = datetime.now() - timedelta(days=1)
        date = yesterday.strftime('%d-%m-%Y')
    location = ad.find_element(By.CLASS_NAME, "location").text.replace(crude_date, '')

    try:
        bedrooms = ad.find_element(By.CLASS_NAME, "bedrooms").text
    except NoSuchElementException:
        bedrooms = ""
    description = ad.find_element(By.CLASS_NAME, "description").text
    crude_price = ad.find_element(By.CLASS_NAME, "price").text
    if "$" in crude_price:
        price = crude_price[1:]
        currency = crude_price[0]
    else:
        price = crude_price
        currency = ""
    apartment_information = {'image': image, 'title': title, 'location': location, 'date': date, 'bedrooms': bedrooms,
                             'description': description, 'price': price, 'currency': currency}
    return apartment_information


if __name__ == '__main__':
    main()
