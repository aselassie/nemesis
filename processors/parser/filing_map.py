from lxml import etree
import requests
import pandas as pd
from bs4 import BeautifulSoup


def read_xml(link):
    r = requests.get(f"{link}")
    doc = r.text
    print(link)
    try:
        root = etree.fromstring(doc)
    except ValueError:
        xml = bytes(bytearray(doc, encoding='utf-8'))
        root = etree.XML(xml)
    key = list(root.nsmap.keys())[0]
    ns = f"{{{root.nsmap[key]}}}"

    all_rows = []

    for child in root:
        name_of_issuer = child.find(f"{ns}nameOfIssuer").text
        title_of_class = child.find(f"{ns}titleOfClass").text
        cusip = child.find(f"{ns}cusip").text
        value = child.find(f"{ns}value").text
        number_of_shares = child.find(f"{ns}shrsOrPrnAmt").find(f"{ns}sshPrnamt").text
        sh = child.find(f"{ns}shrsOrPrnAmt").find(f"{ns}sshPrnamtType").text
        investment_discretion = child.find(f"{ns}investmentDiscretion").text
        voting_authority_sole = child.find(f"{ns}votingAuthority").find(f"{ns}Sole").text
        voting_authority_shared = child.find(f"{ns}votingAuthority").find(f"{ns}Shared").text
        voting_authority_none = child.find(f"{ns}votingAuthority").find(f"{ns}None").text

        single_row = dict(
            name_of_issuer=name_of_issuer,
            title_of_class=title_of_class,
            cusip=cusip,
            value=value,
            number_of_shares=number_of_shares,
            sh=sh,
            investment_discretion=investment_discretion,
            voting_authority_sole=voting_authority_sole,
            voting_authority_shared=voting_authority_shared,
            voting_authority_none=voting_authority_none
        )
        all_rows.append(single_row)
    output_df = pd.DataFrame(all_rows)
    return output_df


def add_ticker_to_filing(raw_13f, cusip_map):
    mapped_13_f = raw_13f.set_index("cusip").join(cusip_map)
    return mapped_13_f.reset_index()


def get_links_from_cik(cik):
    hostname = "https://www.sec.gov/cgi-bin/browse-edgar"
    link = f"{hostname}?action=getcompany&CIK={cik}&type=13F-HR%25&dateb=&owner=include&start=0&count=40&output=atom"
    r = requests.get(f"{link}")
    doc = r.text
    root = etree.fromstring(bytes(doc, encoding='utf-8'))
    ns = f"{{{root.nsmap[None]}}}"
    entries = root.findall(f"{ns}entry")
    all_links = []
    for entry in entries:
        single_entry_link = entry.find(f"{ns}content").find(f"{ns}filing-href").text
        all_links.append(single_entry_link)
    return all_links


def get_xml_links_from_table_link(single_link):
    soup = BeautifulSoup(requests.get(single_link).text, 'html.parser')
    table = soup.find("table")
    all_rows = []
    for row in table.findAll("tr"):
        single_row = []
        for i, cell in enumerate(row.findAll("td")):
            if i == 2:
                single_row.append((cell.find("a", href=True)['href']))
                single_row.append(cell.find("a", href=True).text)
            else:
                single_row.append(cell.text)
        all_rows.append(single_row)
    all_rows = pd.DataFrame(all_rows).dropna(how="all")
    all_rows.loc[:, 6] = [s[-1] for s in all_rows.iloc[:, 3].str.split(".")]
    xml_rows = all_rows[all_rows.iloc[:, 6] == 'xml']
    try:
        infotable_link = xml_rows[xml_rows.iloc[:, 4].str.upper() == 'INFORMATION TABLE'].iloc[0, 2]
    except IndexError:
        file_format = all_rows[all_rows.iloc[:, 4].str.upper().str.contains('13F')].iloc[0, 6]
        if file_format == 'txt':
            return {"infotable_link": None, "primary_doc_link": None}
    primary_doc_link = xml_rows[xml_rows.iloc[:, 4].str.upper().str.contains('13F')].iloc[0, 2]
    infotable_link = f"https://www.sec.gov{infotable_link}"
    primary_doc_link = f"https://www.sec.gov{primary_doc_link}"
    return {"infotable_link": infotable_link, "primary_doc_link": primary_doc_link}


def get_date_from_xml(link):
    r = requests.get(link)
    doc = r.text
    root = etree.fromstring(bytes(doc, encoding='utf-8'))
    ns = f"{{{root.nsmap[None]}}}"
    report_date = root.find(f'{ns}headerData').find(f"{ns}filerInfo").find(f"{ns}periodOfReport").text
    return report_date


def read_xml_dictionary(links_dictionary):
    data_output = read_xml(links_dictionary['infotable_link']).set_index("cusip")
    report_date = get_date_from_xml(links_dictionary['primary_doc_link'])
    data_output.loc[:, "report_date"] = report_date
    return data_output


def get_all_filings(cik, last_n=None):
    single_fund_collection = []
    all_links = get_links_from_cik(cik)[:last_n]
    for link in all_links:
        single_dictionary = get_xml_links_from_table_link(link)
        if single_dictionary['infotable_link'] and single_dictionary['primary_doc_link']:
            single_fund_collection.append(single_dictionary)

    all_filings = []
    for single_dictionary in single_fund_collection:
        single_df = read_xml_dictionary(single_dictionary)
        all_filings.append(single_df)
    all_filings = pd.concat(all_filings)
    all_filings.loc[:, "report_date"] = pd.to_datetime(all_filings.report_date).dt.date
    return all_filings
