import requests
from bs4 import BeautifulSoup
import csv
import re
import time
import asyncio
import aiohttp

CONCURRENT_REQUESTS = 5 # Adjust based on desired parallel requests

sem = asyncio.Semaphore(CONCURRENT_REQUESTS)

PAYLOAD = {}
HEADERS = {
    'Cookie': '_session_id2=788c4bf1fd3f1d8c1c30e54a41db963c; ccsid=506-8000176-9337446; locale=en; logged_out_browsing_page_count=1'
    }

BASE_URL = "https://www.goodreads.com/book/show/"

async def fetch_by_id_async(session, id):
    print(f"Scraping ID: {id}")
    async with session.get(BASE_URL + id) as response:
        wrapper = id, await response.text()
        return wrapper

def fetch_by_id(id: str):
    if not id:
        print("BAD ID")
        return
    
    url = BASE_URL + id


    response = requests.request("GET", url, headers=HEADERS, data=PAYLOAD)

    return response.text


def parse_html(html: str):
    """Parse the HTML and extract relevant data."""
    id = None
    avg_rating = None
    genres = None
    rating_count = None

    soup = BeautifulSoup(html, "lxml")
    rating_div = soup.find("div", class_="RatingStatistics__rating")
    rating_text = rating_div.get_text(strip=True) if rating_div else None

    script_tag = soup.find("script", id="__NEXT_DATA__")
    if script_tag:
        data = script_tag.text
        # with open("test-script.txt", "w") as f:
        #     f.write(data)\

        #IDs
        pattern = r'"book_id":"(\d+)"'
        match = re.search(pattern, data)
        if match:
            id = match.group(1)
        

        #Genres
        pattern = r'"__typename"\s*:\s*"Genre"\s*,\s*"name"\s*:\s*"(.*?)"'
        match = re.findall(pattern, data)
        if match:
            genres = match
        
        #Rating Count
        pattern = r'"ratingsCount":(\d+),'
        match = re.search(pattern, data)
        if match:
            rating_count = match.group(1)
        
        #Average Rating
        pattern = r'"averageRating"\s*:\s*([\d.]+)'
        match = re.search(pattern, data)
        if match:
            avg_rating = match.group(1)

    output = {"id": str(id),
              "avg_rating": str(avg_rating),
              "genres": str(genres),
              "rating_count": str(rating_count)}
    
    if any(value is None for value in output.values()):
        print(f"Missing data for ID: {id}")
    return output

async def main():
    start = time.time()
    OUTPUT_FILE = "output.csv"
    INPUT_FILE = "book_ids_to_scrape.txt"
    HTMLList = {}
    dataList = []
    doneIds = set()
    with open(INPUT_FILE) as f:
        async with aiohttp.ClientSession() as session:
            tasks = [fetch_by_id_async(session, re.match(r"^\d+(?=\.)", line).group()) for line in f]
            results = await asyncio.gather(*tasks)
        for res in results:
            id, html = res
            if html:    
                HTMLList[id] = html
            else:
                print(f"Failed to scrape ID: {id}")
    failedIds = []
    for id in HTMLList.keys():
        if id not in doneIds:
                data = parse_html(HTMLList[id])
                if any(value is None for value in data.values()):
                    failedIds.append(id)
                else:
                    dataList.append(data)
                    doneIds.add(id)
        else:
            if id in doneIds:
                print(f"ID {id} already scraped")
            else:
                print(f"Failed to scrape ID: {id}")
        if(len(doneIds) % 5 == 0):
            print("Time elapsed: ", time.time() - start)
            print(f"\nScrape rate: {len(dataList) / (time.time() - start)}\n")

        
    with open(OUTPUT_FILE, mode="w", newline="", encoding="utf-8") as csvfile:
        fieldnames = dataList[0].keys()
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(dataList)


if __name__ == "__main__":
    asyncio.run(main())
