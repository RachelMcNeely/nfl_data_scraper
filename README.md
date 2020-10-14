# nfl_data
A database and scrapers to hold nfl data such as injuries and player information.

### To run the scraper and update the database:
To update a certain year, you can pass the year parameter in as an argument.
  ```
  scrapy crawl injuries -a year=2020
  ```
If you don't pass a year in as an argument, then it will default to 2020. (TO DO: Default to update all years.)
  ```
  scrapy crawl injuries
  ```
