# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

import datetime

from .psql import connect
from scrapy.conf import settings

table_name = settings.get('ESPN_TABLE')


class FantasyDataSpiderPipeline(object):
    def __init__(self):
        pass

    def open_spider(self, spider):
        self.conn = connect()
        drop_table = """DROP TABLE IF EXISTS """ + table_name
        create_table = """CREATE TABLE IF NOT EXISTS """ + table_name + """ ( ffl_source varchar, playername varchar, team varchar, pos varchar,
          status_type varchar, passing_c float, passing_a float, passing_yds float, passing_td float,
          passing_int float, rushing_r float, rushing_yds float, rushing_td float, receiving_rec float,
          receiving_yds float, receiving_tot float, pts_total float, parsed_on varchar
          );"""
        with self.conn:
            with self.conn.cursor() as cur:
                cur.execute(drop_table)
                cur.execute(create_table)
                self.conn.commit()

    def close_spider(self, spider):
        self.conn.close()

    def process_item(self, item, spider):
        sql = """
            INSERT INTO """ + table_name + """ ( ffl_source, playername, team, pos,
              status_type, passing_c, passing_a, passing_yds, passing_td,
              passing_int, rushing_r, rushing_yds, rushing_td, receiving_rec,
              receiving_yds, receiving_tot, pts_total, parsed_on
            )
            VALUES ( %(ffl_source)s, %(playername)s, %(team)s, %(pos)s,
              %(status_type)s, %(passing_c)s, %(passing_a)s, %(passing_yds)s,
              %(passing_td)s, %(passing_int)s, %(rushing_r)s, %(rushing_yds)s,
              %(rushing_td)s, %(receiving_rec)s, %(receiving_yds)s,
              %(receiving_tot)s, %(pts_total)s, %(parsed_on)s
            );
        """
        item['parsed_on'] = datetime.datetime.now()

        with self.conn:
            with self.conn.cursor() as cur:
                cur.execute(sql, item)
                self.conn.commit()

        return item
