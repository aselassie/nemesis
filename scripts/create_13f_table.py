import pandas as pd
from core.models import TickerMap, Security, HedgeFund, Filing
from django.db import transaction
from processors.parser.filing_map import get_all_filings


@transaction.atomic
def get_security_id(security_list):
    all_ids = [Security.objects.get_or_create(ticker=s)[0].pk for s in security_list]
    output = pd.DataFrame([security_list, all_ids], index=['ticker', 'security_id']).T
    return output


def save_filing_set_to_db(cik, all_filings):
    cusip_map = pd.DataFrame(TickerMap.objects.all().values("cusip", 'ticker', "as_of_date"))
    cusip_map = cusip_map.sort_values("as_of_date").groupby('cusip').last().reset_index()
    cusip_map = cusip_map.drop("as_of_date", axis=1).set_index("cusip")
    all_filings = all_filings.join(cusip_map)
    tickers = all_filings.ticker.unique().tolist()
    ticker_map = get_security_id(tickers).set_index("ticker")
    all_filings = all_filings.join(ticker_map, on='ticker').drop("ticker", axis=1)
    fund_id = HedgeFund.objects.get(cik=cik).pk
    all_filings.loc[:, 'hedge_fund_id'] = fund_id
    report_dates = all_filings.report_date.unique().tolist()
    Filing.objects.filter(hedge_fund_id=fund_id,report_date__in=report_dates).delete();
    filing_set = [Filing(**s) for s in all_filings.reset_index().to_dict("records")]
    Filing.objects.bulk_create(filing_set);


def run():
    cik_list = ['0001680964', '0001317583', '0001569064']
    for cik in cik_list:
        print(cik)
        all_filings = get_all_filings(cik)
        save_filing_set_to_db(cik, all_filings)
