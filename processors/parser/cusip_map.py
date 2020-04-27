import pandas as pd
from urllib.error import HTTPError
from zipfile import ZipFile
from urllib.request import urlopen
import io
from core.models import TickerMap


def parse_fail_to_deliver(url):
    print(url)
    try:
        url = urlopen(f"https://www.sec.gov/files/data/fails-deliver-data/cnsfails{url}.zip")
    except HTTPError:
        try:
            url = urlopen(f"https://www.sec.gov/files/data/fails-deliver-data/cnsfails{url}_0.zip")
        except HTTPError:
            url = urlopen(
                f"https://www.sec.gov/files/data/frequently-requested-foia-document-fails-deliver-data/cnsfails{url}.zip")
    bytes_file = url.read()
    zipped_file  = io.BytesIO(bytes_file)

    zipfile = ZipFile(zipped_file)

    filename = zipfile.namelist()[0]

    txt = zipfile.read(filename)

    cusip_map = pd.read_csv(io.BytesIO(txt), sep="|", encoding="ISO-8859-1")

    cusip_map = cusip_map[['CUSIP', 'SYMBOL']].dropna().drop_duplicates()
    print("Parsed")
    return cusip_map


def generate_cusip_map(start_date, end_date):
    daterange = pd.date_range(start=start_date, end=end_date, freq="M")
    daterange = daterange.strftime("%Y%m")
    search_list = []
    for month in daterange:
        for letter in ['a', 'b']:
            search_str = f"{month}{letter}"
            search_list.append(search_str)

    all_maps = pd.DataFrame()
    for entry in search_list:
        single_map = parse_fail_to_deliver(entry)
        all_maps = pd.concat([all_maps, single_map]).drop_duplicates()
    all_maps.columns = ['cusip', 'symbol']
    all_maps = all_maps.drop_duplicates()
    all_maps = all_maps.set_index("cusip")
    return all_maps


def save_to_db(output):
    cleaned_output = output.reset_index().rename({"symbol": "ticker"}, axis=1)
    existing = pd.DataFrame(TickerMap.objects.all().values("cusip", 'ticker', "id"))
    if not existing.empty:
        existing = existing.set_index(['cusip', 'ticker'])
        merged = cleaned_output.set_index(['cusip', 'ticker']).join(existing)
        merged = merged[~merged.id.isnull()].drop("id", axis=1)
        merged = merged.reset_index().to_dict(orient='records')
    else:
        merged = cleaned_output.reset_index().to_dict(orient='records')
    new_entries = []
    for single_entry in merged:
        new_ticker = TickerMap(ticker=single_entry['ticker'], cusip=single_entry['cusip'])
        new_entries.append(new_ticker)
    TickerMap.objects.bulk_create(new_entries)


def generate_and_save(start_date, end_date):
    output = generate_cusip_map(start_date, end_date)
    save_to_db(output)
