# Goodreads scraper
Created this cause https://github.com/maria-antoniak/goodreads-scraper/ was broken

# Prerequisites
Python3, BeautifulSoup4, aiohttp (only required for the async version)

# Usage
`scraper.py` is for sequential scraping, around 1 id per second speed

`scraper-aync.py` is for asynchronous scraping, around 10 per second speed. (You can adjust the semaphore count depending on your network

Both occasionally will fail (Output None on some rows) so be aware. You can tell which ids failed by line location relative to others.
Often the async version might struggle if the semaphore count is too high and fail around 1/2 requests per 100.

So basically just edit `INPUT_FILE` and `OUTPUT_FILE` in each script and run

The input file should contain either a list of ids separated by line or id and name

Ex: Both work.

9265453.Embassytown

16090981.Thief

13067.Flush

793399.Stray



OR


9265453

16090981

13067

793399

