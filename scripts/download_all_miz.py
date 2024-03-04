""" 
Downloads all MIZ shapefiles from this link: https://usicecenter.gov/Products/ArchiveSearchMulti?table=DailyArcticShapefiles

To run:
pixi run python scripts/download_all_miz.py
"""
import os
from datetime import datetime

import requests
from bs4 import BeautifulSoup


def format_date(date_obj: datetime) -> str:
    """Function to format date in MM/DD/YYYY format"""
    return date_obj.strftime("%m/%d/%Y")


def get_date(string: str) -> str:
    """From file link, extract date for MIZ product"""
    date_str = string.split("=")[1][1:]
    if len(date_str) != 8:
        raise ValueError(
            "The date string must be 8 characters long in the form 'MMDDYYYY'."
        )

    # Extract parts of the date
    mm = date_str[:2]
    dd = date_str[2:4]
    yyyy = date_str[4:]

    # Construct the new date string in 'YYYYMMDD' format
    new_date_str = yyyy + mm + dd

    return new_date_str


def download_miz_files(
    start_date: datetime, end_date: datetime, directory: str
) -> None:
    """Function to download MIZ files from the website"""
    search_url = "https://usicecenter.gov/Products/DisplaySearchResults"
    base_url = "https://usicecenter.gov"

    # The link requires filling out a form for the date range.
    # Adjust these parameters based on the form data required for MIZ files.
    form_data = {
        "searchText": "DailyArcticShapefiles",
        "searchProduct": "Arctic MIZ Shapefile",
        "startDate": format_date(start_date),
        "endDate": format_date(end_date),
    }

    headers = {"Content-Type": "application/x-www-form-urlencoded"}

    with requests.Session() as session:
        response = session.post(search_url, data=form_data, headers=headers)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")

        file_links = [
            a["href"]
            for a in soup.find_all("a", href=True)
            if "DownloadArchive" in a["href"]
        ]

        if not os.path.exists(directory):
            os.makedirs(directory)

        for file_link in file_links:
            full_url = base_url + file_link
            datestring = get_date(file_link.split("/")[-1])
            file_name = f"nic_miz{datestring}nc_pl_a.zip"
            file_path = os.path.join(directory, file_name)

            file_response = session.get(full_url)
            if not os.path.exists(file_path):
                with open(file_path, "wb") as file:
                    file.write(file_response.content)
                print(f"Downloaded {file_name}")
            else:
                print(f"{file_name} already on disk, skipping download...")


if __name__ == "__main__":
    start_date = datetime(2014, 12, 14)  # Adjust start date as needed
    end_date = datetime.now()
    directory = "data/MIZ_Files"
    download_miz_files(start_date, end_date, directory)
