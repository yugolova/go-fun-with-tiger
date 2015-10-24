# go-fun-with-tiger

Scrapy project dedicated to  30th anniversary of "Calvin and Hobbes"  by Bill Watterson. Yey!


You can download pictures for a given year and month 

```
scrapy crawl calvin_and_hobbes_pics -a year=2015 -a month=2
```
...or just get them all at once

```
scrapy crawl calvin_and_hobbes_pics -a _all=True
```

Enjoy 30 years of fun :)

http://www.gocomics.com/calvinandhobbes
