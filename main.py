import requests
from bs4 import BeautifulSoup
import pandas as pd
from time import sleep
import json


def log_status(website_url, url_counter):
    with open('scraping_log.txt', 'a', encoding='utf-8') as log_file:
        log_file.write(f"Processed URL {url_counter}: {website_url}\n")
        print(f"Logged URL {url_counter}: {website_url}")

def main():
    companies_data = []
    from_page = 1
    to_page = 1000000000
    url_counter = 1

    # lets get company urls from the url-master.csv file in root directory
    # with open('url-master.csv', 'r', encoding='utf-8') as file:
    with open('test.csv', 'r', encoding='utf-8') as file:
        next(file) 
        lines = file.readlines()
        for line in lines: 
            line_stripped = line.strip()
            if not line_stripped:
                continue

            all_reviews_for_current_company = []

            try:
                # Name,Website,Address,Category,TrustScore,Reviews
                company_parts = line.strip().split(',')
                company_name = company_parts[0].strip() 
                website_url = company_parts[1].strip()
                address = company_parts[2].strip()
                category = company_parts[3].strip()
                trust_score = company_parts[4].strip()
                reviews_count = company_parts[5].strip()
                for page in range(from_page, to_page):
                    print(f"Scraping page {page} for company: {company_name}...")
                    res_url = f"https://www.trustpilot.com/review/{website_url}?page={page}"
                    response = requests.get(res_url)
                    soup = BeautifulSoup(response.content, 'html.parser')
                    review_articles = soup.find_all('article', class_='styles_reviewCard__Qwhpy')
                    # print(f"Found {len(review_articles)} reviews on page {page}.")
                    if not review_articles:
                        # print(f"No reviews found on page {page}. Ending scraping.")
                        break
                    for article in review_articles:
                        try:
                            username = article.find('span', class_='typography_heading-xs__osRhC').text.strip()
                        except:
                            username = None
                        try:
                            date_tag = article.find('time')
                            date = date_tag.text.strip() if date_tag else None
                        except:
                            date = None
                        try:
                            rating_div = article.find('div', class_='styles_reviewHeader__DzoAZ')
                            rating = rating_div['data-service-review-rating'] if rating_div and rating_div.has_attr('data-service-review-rating') else None
                        except:
                            rating = None
                        try:
                            title = article.find('h2').text.strip()
                        except:
                            title = None
                        try:
                            paragraphs = article.select('p.typography_body-l__v5JLj')
                            content = paragraphs[0].text.strip() if paragraphs else None
                        except:
                            content = None

                        all_reviews_for_current_company.append({
                            'Username': username,
                            'Total Reviews': rating,
                            'Posted Date': date,
                            'Rating': rating,
                            'Title': title,
                            'Content': content
                        })
                    # let's have a dynamic sleep to avoid being blocked
                    from random import randint
                    sleep(randint(1, 3))
                reviews_json_string = json.dumps(all_reviews_for_current_company)
                companies_data.append({
                    'Company Name': company_name,
                    'Website': website_url, # Store the base URL segment
                    'Address': address,
                    'Category': category,
                    'Trust Score': trust_score,
                    'Reviews Count': reviews_count,
                    'Reviews': reviews_json_string # This will be the JSON column
                }) 
                # After processing all companies, create the final DataFrame
                # After processing all companies, create the final DataFrame and save to CSV
                if companies_data:
                    log_status(website_url,url_counter)
                    url_counter += 1
                    df = pd.DataFrame(companies_data)
                    df.head()
                    df.to_csv('trustpilot_reviews.csv', index=False)
                    sleep(randint(1,3))  # Sleep for a second before processing the next company
                else:
                    print("\nNo company data was successfully scraped.")
            except IndexError:
                print(f"Error: Line '{line_stripped}' in 'test.csv' does not have enough columns or malformed. Skipping.")
            except Exception as e:
                print(f"An unexpected error occurred for line '{line_stripped}': {e}. Skipping to next company.")
                continue # Skip to the next line in the CSV

if __name__ == "__main__":
    main()
    print("Scraping completed. Check 'trustpilot_reviews.csv' for results.")