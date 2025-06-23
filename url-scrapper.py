from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import pandas as pd
import time
import json
import os
# === Load category list from JSON ===
with open("trustpilot_categories.json", "r", encoding="utf-8") as file:
    categories = json.load(file)

# === Setup WebDriver ===
options = Options()
options.add_argument("--headless=new")
driver = webdriver.Chrome(options=options)

# === Loop through each category ===
for category in categories:
    print(f"\n--- Processing Category: {category['name']} ---")
    driver.get(category["url"])

    # Accept cookies (once)
    try:
        WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.ID, "onetrust-accept-btn-handler"))
        ).click()
    except:
        pass  # Already accepted or not visible

    category_data = []
    zero_review_pages = 0
    page_number = 0
    file_path = f"{category['name']}_data.csv"

    # Remove existing file if starting fresh
    if os.path.exists(file_path):
        os.remove(file_path)

    while True:
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.CDS_Card_card__16d1cc"))
            )

            cards = driver.find_elements(By.CSS_SELECTOR, "div.CDS_Card_card__16d1cc")
            page_has_reviews = False
            page_rows = []

            for card in cards:
                try:
                    name = card.find_element(By.CSS_SELECTOR, "p.CDS_Typography_heading-s__bedfe1").text if card.find_elements(By.CSS_SELECTOR, "p.CDS_Typography_heading-s__bedfe1") else ""
                    url = card.find_element(By.CSS_SELECTOR, "p.styles_websiteUrlDisplayed__e1szC").text if card.find_elements(By.CSS_SELECTOR, "p.styles_websiteUrlDisplayed__e1szC") else ""
                    rating = card.find_element(By.CSS_SELECTOR, "div.styles_rating__DdF22 img").get_attribute("alt") if card.find_elements(By.CSS_SELECTOR, "div.styles_rating__DdF22 img") else ""
                    reviews = card.find_element(By.CSS_SELECTOR, "span[data-business-unit-review-count='true']").text if card.find_elements(By.CSS_SELECTOR, "span[data-business-unit-review-count='true']") else ""
                    address = card.find_element(By.CSS_SELECTOR, "div.styles_businessLocation__UXz5s p").text if card.find_elements(By.CSS_SELECTOR, "div.styles_businessLocation__UXz5s p") else ""

                    if reviews and reviews != "0":
                        page_has_reviews = True

                    page_rows.append({
                        "Name": name,
                        "Website": url,
                        "TrustScore": rating,
                        "Reviews": reviews,
                        "Address": address
                    })

                    print(f"{name} | {url}")

                except Exception as e:
                    print(f"Skipping a card due to error: {e}")
                    continue

            if not page_has_reviews:
                zero_review_pages += 1
                print(f"⚠️ Page with no reviews. Total zero-review pages: {zero_review_pages}")
            else:
                zero_review_pages = 0

            if zero_review_pages >= 3:
                print(f"❌ Skipping category '{category['name']}' due to 3 consecutive zero-review pages.")
                break

            # Append page data to main data
            category_data.extend(page_rows)

            # ✅ Save after each page
            if page_rows:
                page_number += 1
                write_mode = 'w' if not os.path.exists(file_path) else 'a'
                write_header = not os.path.exists(file_path)
                df = pd.DataFrame(page_rows)
                df.to_csv(file_path, index=False, mode=write_mode, header=write_header)
                print(f"✅ Saved page {page_number} to {file_path} | Total rows: {len(category_data)}")

            # Log progress
            with open("progress.log", "a", encoding="utf-8") as log_file:
                log_file.write(f"{category['name']} - Page {page_number} written - Total: {len(category_data)} rows\n")

            # Try clicking "Next page"
            try:
                next_btn = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((By.XPATH, "//a[@aria-label='Next page']"))
                )
                next_btn.click()
                time.sleep(3)
            except:
                print("No more pages.")
                break

        except Exception as e:
            print(f"Failed to load cards: {e}")
            break

    print(f"✅ Finished category '{category['name']}' with {len(category_data)} total entries.")

# # === Loop through each category ===
# for category in categories:
#     print(f"\n--- Processing Category: {category['name']} ---")
#     driver.get(category["url"])

#     # Accept cookies (once)
#     try:
#         WebDriverWait(driver, 5).until(
#             EC.element_to_be_clickable((By.ID, "onetrust-accept-btn-handler"))
#         ).click()
#     except:
#         pass  # Already accepted or not visible

#     category_data = []
#     zero_review_pages = 0

#     while True:
#         try:
#             # Wait for business cards to load
#             WebDriverWait(driver, 10).until(
#                 EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.CDS_Card_card__16d1cc"))
#             )

#             cards = driver.find_elements(By.CSS_SELECTOR, "div.CDS_Card_card__16d1cc")
#             page_has_reviews = False

#             for card in cards:
#                 try:
#                     try:
#                         name = card.find_element(By.CSS_SELECTOR, "p.CDS_Typography_heading-s__bedfe1").text
#                     except:
#                         name = ""
#                     try:
#                         url = card.find_element(By.CSS_SELECTOR, "p.styles_websiteUrlDisplayed__e1szC").text
#                     except:
#                         url = ""
#                     try:
#                         rating = card.find_element(By.CSS_SELECTOR, "div.styles_rating__DdF22 img").get_attribute("alt")
#                     except:
#                         rating = ""
#                     try:
#                         reviews = card.find_element(By.CSS_SELECTOR, "span[data-business-unit-review-count='true']").text
#                     except:
#                         reviews = ""
#                     try:
#                         address = card.find_element(By.CSS_SELECTOR, "div.styles_businessLocation__UXz5s p").text
#                     except:
#                         address = ""

#                     if reviews and reviews != "0":
#                         page_has_reviews = True
#                     print(f"{name} | {url}")

#                     category_data.append({
#                         "Name": name,
#                         "Website": url,
#                         "TrustScore": rating,
#                         "Reviews": reviews,
#                         "Address": address
#                     })

#                 except Exception as e:
#                     print(f"Skipping a card due to error: {e}")
#                     continue
#             # If no cards had reviews, count it as a 0-review page
#             if not page_has_reviews:
#                 zero_review_pages += 1
#                 print(f"⚠️ Page with no reviews. Total zero-review pages: {zero_review_pages}")
#             else:
#                 zero_review_pages = 0  # reset counter if we got reviews

#             if zero_review_pages >= 3:
#                 print(f"❌ Skipping category '{category['name']}' due to 3 consecutive zero-review pages.")
#                 category_data = []  # discard collected data (optional)
#                 break

#             # Try clicking "Next page"
#             try:
#                 next_btn = WebDriverWait(driver, 5).until(
#                     EC.element_to_be_clickable((By.XPATH, "//a[@aria-label='Next page']"))
#                 )
#                 next_btn.click()
#                 time.sleep(3)
#             except:
#                 print("No more pages.")
#                 break
#             print(f"Processed {len(category_data)} cards so far in {category['url']} category.")        
#         except Exception as e:
#             print(f"Failed to load cards: {e}")
#             break
#     #lets write the data to a csv file in this format, name, website, trustscore, reviews, address
#     df = pd.DataFrame(category_data)
#     df.to_csv(f"data.csv", index=False)
#     print(f"Total cards processed in {category['name']}: {len(category_data)}")



#     # Save extracted data into the category object
#     category["data"] = category_data

# # === Close the driver ===
# driver.quit()

# # === Save updated JSON ===
# # with open("trustpilot_categories.json", "w", encoding="utf-8") as f:
# #     json.dump(categories, f, indent=4, ensure_ascii=False)

# # print("\n✅ All categories processed and saved to trustpilot_categories.json")

# # Save to CSV
# # df = pd.DataFrame(data)
# # df.to_csv("scraped_data.csv", index=False)
# # print("Data saved to scraped_data.csv")
