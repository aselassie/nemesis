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
    dates_list = pd.date_range(start=start_date, end=end_date, freq="M")
    expanded_date_list = []
    daterange = dates_list.strftime("%Y%m")
    search_list = []
    for i, month in enumerate(daterange):
        for letter in ['a', 'b']:
            search_str = f"{month}{letter}"
            search_list.append(search_str)
            expanded_date_list.append(dates_list[i])

    all_maps = pd.DataFrame()
    for time_stamp, entry in zip(expanded_date_list, search_list):
        single_map = parse_fail_to_deliver(entry)
        single_map.loc[:, "date"] = time_stamp
        all_maps = pd.concat([all_maps, single_map]).drop_duplicates()
    all_maps.columns = ['cusip', 'ticker', 'as_of_date']
    all_maps = all_maps.drop_duplicates()
    all_maps = all_maps.set_index("cusip")
    return all_maps


def save_to_db(output):
    cleaned_output = output.reset_index().groupby(["cusip", 'ticker']).last().reset_index()
    ticker_set = cleaned_output.to_dict("records")
    existing = pd.DataFrame(TickerMap.objects.values("ticker", "cusip"))
    if not existing.empty:
        existing = (existing['ticker'] + "-" + existing['cusip']).values.tolist()
        filtered_ticker_set = [entry for entry in ticker_set if f"{entry['ticker']}-{entry['cusip']}" not in existing]
    else:
        filtered_ticker_set = ticker_set
    TickerMap.objects.bulk_create([TickerMap(**s) for s in filtered_ticker_set])


def generate_and_save(start_date, end_date):
    output = generate_cusip_map(start_date, end_date)
    save_to_db(output)
