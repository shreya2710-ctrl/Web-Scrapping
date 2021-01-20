#!/usr/bin/env python
# -*- coding: utf-8 -*-
import scrapy
from sqlalchemy import create_engine, and_, text
from sqlalchemy.orm import sessionmaker, exc
from databasesetup import *
import datetime


engine = create_engine('sqlite:///scrape.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind = engine)
dbsession = DBSession()


class Spider(scrapy.Spider):
    name = 'reddit'
    def start_requests(self):
        url ='reddit.com'
        yield scrapy.Request(url=url, callback=self.parse)
# overall -> <div class="postContainer">
# catch_id -> automatic
# message -> <blockquote>
# author -> <span class="name">"
# catchdate -> datetime.now
# website -> htpp://www.reddit.com
    def parse(self, response):
        count = 0
        comments = response.css(".postContainer")
        words = [w.word for w in dbsession.query(Buzzwords.word)] # get list of buzzwords
        for word in words:
            for comment in comments:
                message = comment.css(".post").xpath("./blockquote/text()").extract_first() # extract comment
                if message == None:
                    message = ""
                if word in message.lower():
                    authorName = comment.css("span.name::text").extract_first()
                    authorNo = comment.css('a[title="Reply to this post"]::text').extract_first()
                    author = authorName+" "+authorNo
# add to database
                    new_catch = Catches(message=message, author=author, word=word, catchdate=datetime.datetime.now().strftime("%Y-%m-%d %H-%M-%S"), website=u"http://www.4chan.org")
                    dbsession.add(new_catch)
                    dbsession.commit()
                    count+=1
        self.log('Finished scraping. Found {0} possible occurrences'.format(count))