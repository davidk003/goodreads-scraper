import requests
from bs4 import BeautifulSoup
import csv
import re
import time

BASE_URL = "https://www.goodreads.com/book/show/"
def fetch_by_id(id: str):
    if not id:
        print("BAD ID")
        return
    
    url = BASE_URL + id

    payload = {}
    headers = {
    'Cookie': '_session_id2=788c4bf1fd3f1d8c1c30e54a41db963c; ccsid=506-8000176-9337446; locale=en; logged_out_browsing_page_count=1'
    }

    response = requests.request("GET", url, headers=headers, data=payload)

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

def main():
    start = time.time()
    OUTPUT_FILE = "output.csv"
    INPUT_FILE = "goodreads_classics_sample.txt"
    dataList = []
    doneIds = set()
    with open(INPUT_FILE) as f:
        for line in f:
            nonNumLine = re.match(r"^\d+(?=\.)", line).group()
            print(f"Scraping ID: {nonNumLine}")
            html = fetch_by_id(nonNumLine)
            
            if html and nonNumLine not in doneIds:
                data = parse_html(html)
                dataList.append(data)
                doneIds.add(nonNumLine)
            else:
                if nonNumLine in doneIds:
                    print(f"ID {nonNumLine} already scraped")
                else:
                    print(f"Failed to scrape ID: {nonNumLine}")
            print("Time elapsed: ", time.time() - start)
            if(len(doneIds) % 5 == 0):
                print(f"\nScrape rate: {len(dataList) / (time.time() - start)}\n")
        
    with open(OUTPUT_FILE, mode="w", newline="", encoding="utf-8") as csvfile:
        fieldnames = dataList[0].keys()
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(dataList)


if __name__ == "__main__":
    main()
