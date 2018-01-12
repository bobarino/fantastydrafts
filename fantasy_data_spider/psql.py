import psycopg2

from scrapy.conf import settings

def connect():
    return psycopg2.connect(
        user=settings.get('PG_USER'),
        dbname=settings.get('PG_DBNAME'),
        host=settings.get('PG_HOST'),
        password=settings.get('PG_PASSWORD')
    )
