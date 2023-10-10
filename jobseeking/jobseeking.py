import enum
from selenium import webdriver
import time
from selenium.webdriver.common.by import By
import jobseeking.constants as const

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import pandas as pd


class Jobseeking(webdriver.Edge):
    def __init__(self) -> None:
        super(Jobseeking, self).__init__()
        # self.implicitly_wait(30)
        self.maximize_window()

    def land_first_page(self):
        self.get(const.BASE_URL)

    def get_job_content(self, job_link, job_date):
        data = {}
        data['link'] = job_link
        data['date'] = job_date

        job_content = WebDriverWait(self, 10).until(
            EC.presence_of_element_located(
                (
                    By.XPATH,
                    '//div[@id="jobsearch-ViewjobPaneWrapper"]/div'
                )
            )
        )

        h2_elements = job_content.find_element(
            by=By.XPATH,
            value='.//h2[1]'
        )

        data['title'] = h2_elements.text.split('\n')[0]

        data['company'] = job_content.find_element(
            by=By.CSS_SELECTOR,
            value='div[data-testid="inlineHeader-companyName"]'
        ).text

        data['location'] = job_content.find_element(
            by=By.CSS_SELECTOR,
            value='div[data-testid = "inlineHeader-companyLocation"]'
        ).text

        # gaji
        try:
            data['gaji'] = job_content.find_element(
                by=By.CSS_SELECTOR,
                value='div[id="salaryInfoAndJobType"]'
            ).text
        except:
            data['gaji'] = "-"

        # DESCRIPTION
        data['job_desc'] = self.find_element(
            by=By.CSS_SELECTOR,
            value='div[id="jobDescriptionText"]'
        ).text.strip()

        # INCLUDE KEYWORD
        include_keyword = []
        for key in const.INCLUDE_KEYWORDS:
            if key.lower() in data['job_desc'].lower():
                include_keyword.append(key)
            elif key.lower() in data['title'].lower():
                include_keyword.append(key)
        data['include_keyword'] = ','.join(
            include_keyword) if len(include_keyword) else '-'

        # EXCLUDE KEYWORD
        exclude_keyword = []
        for key in const.EXCLUDE_KEYWORDS:
            if key.lower() in data['job_desc'].lower():
                exclude_keyword.append(key)
            elif key.lower() in data['title'].lower():
                exclude_keyword.append(key)
        data['exclude_keyword'] = ','.join(
            exclude_keyword) if len(exclude_keyword) else '-'

        print(f"data: {data['title']} - {data['company']}")
        return data

    def check_pagination(self):
        """
        return int, (1=success, 0=fail) 
        """
        print("searching pagination...")
        try:
            # Locating pagination section on page
            pagination = WebDriverWait(self, 5).until(
                EC.presence_of_element_located(
                    (
                        By.CSS_SELECTOR,
                        'nav[aria-label="pagination"]'
                    )
                )
            )

            # Locating pagination section on page
            next_page = WebDriverWait(pagination, 10).until(
                EC.element_to_be_clickable(
                    (
                        By.CSS_SELECTOR,
                        'a[aria-label="Next Page"]'
                    )
                )
            )

            # scroll to pagination section
            self.execute_script(
                "arguments[0].scrollIntoView();", next_page)

            next_page.click()
            print("pagination found!")
            time.sleep(2)
            return 1
        except Exception as e:
            print(f"error: {e}")
            print("pagination not found")
            return 0

    def close_email_subs(self):
        try:
            # Locating pagination section on page
            offer_section = WebDriverWait(self, 10).until(
                EC.element_to_be_clickable(
                    (
                        By.CSS_SELECTOR,
                        'div[id="mosaic-desktopserpjapopup"]'
                    )
                )
            )
            offer_section.find_element(
                by=By.CSS_SELECTOR,
                value='button[aria-label="close"]'
            ).click()
            print("subscription closed")
        except:
            print("no subscription offer")

    def scroll_screen(self, element):
        # scroll to the element
        self.execute_script(
            "arguments[0].scrollIntoView();",
            element
        )
        self.execute_script("window.scrollBy(0, -180);")

    def extract_jobs_page(self):
        # locating job listing div
        WebDriverWait(self, 30).until(
            EC.visibility_of_element_located(
                (
                    By.CSS_SELECTOR,
                    'div[id="mosaic-provider-jobcards"]'
                )
            )
        )

        jobs_section = self.find_element(
            by=By.CSS_SELECTOR,
            value='div[id="mosaic-provider-jobcards"]'
        )

        # locating each job title inside job listing
        jobs = jobs_section.find_elements(
            by=By.XPATH,
            value='./ul/li'
        )
        print(f"result in current page:{len(jobs)}")

        job_df = pd.DataFrame()
        # extract each job
        for job in jobs:
            try:
                h2_element = job.find_element(
                    by=By.CSS_SELECTOR,
                    value="h2"
                )
            except:
                continue

            job_display = h2_element.find_elements(
                by=By.CSS_SELECTOR,
                value="a"
            )

            print(f'a found:{len(job_display)}')
            # for i, _ in enumerate(job_display):
            #     print(f"a-{i}: {_.get_attribute('href')}")

            job_link = job_display[0].get_attribute("href")

            job_date = job.find_element(
                by=By.CLASS_NAME,
                value='date'
            ).text.split('\n')[-1]

            print(f'date: {job_date}')

            self.scroll_screen(job_display[0])

            # click job
            job_display[0].click()

            # check content
            print("checking content...")
            job_content = self.get_job_content(job_link, job_date)
            new_df = pd.DataFrame([job_content])  # Dict to DF
            if job_df.empty:
                job_df = pd.DataFrame(
                    columns=job_content.keys()
                )

            job_df = pd.concat(
                [job_df, new_df],
                axis=0,
                ignore_index=True
            )
            time.sleep(1)

        return job_df
