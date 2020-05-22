from processors.parser.cusip_map import generate_and_save


def run():
    generate_and_save("2013-12-31", "2019-03-31")
