from beancount.core.number import D
from beancount.ingest import importer
from beancount.core import account
from beancount.core import amount
from beancount.core import flags
from beancount.core import data
from beancount.core.position import Cost

import datetime
import csv
import os
import re


class StripeImporter(importer.ImporterProtocol):

    # NOTE: This importer does not like `self` to be used anywhere,
    # hence all staticmethod

    def __init__(self, account, lastfour):
        self.account = account
        self.lastfour = lastfour

    @staticmethod
    def identify(f) -> bool:
        return re.match("[Ss]tripe.*\.csv", os.path.basename(f.name))

    @staticmethod
    def name() -> str:
        return "STRIPE_IMPORTER"

    @staticmethod
    def file_account(f) -> str:
        return os.path.join("~", "tmp", f.name)

    @staticmethod
    def file_name(f) -> str:
        return os.path.basename(f.name)

    @staticmethod
    def file_date(f) -> datetime.date:
        return datetime.date(2022, 11, 5)

    @staticmethod
    def extract(f):
        entries = []

        with open(f.name) as f:
            for index, row in enumerate(csv.DictReader(f)):
                # NOTE: this spits out strings, no conversions
                _type = row["Type"]
                if _type == "charge":
                    total_amount = "-" + row["Amount"]  # e.g. 30
                    fee_amt = row["Fee"]  # e.g. 1.17
                    net_amt = row["Net"]  # e.g. 28.83

                elif _type == "refund":
                    total_amount = row["Amount"][1:]  # e.g. -14.00
                    fee_amt = row["Fee"]  # e.g. 0
                    net_amt = row["Net"]  # e.g. -14.00

                description = "%s: %s" % (row["id"], row["Description"])
                customer_id = row["Source"]
                trans_date = datetime.datetime.strptime(
                    row["Created (UTC)"], "%Y-%m-%d %H:%M"
                ).date()

                meta = data.new_metadata(f.name, index)

                txn = data.Transaction(
                    meta=meta,
                    date=trans_date,
                    flag=flags.FLAG_OKAY,
                    payee="payee",  # both payee and narration get mangled
                    narration="What does this do?",
                    tags=set(),
                    links=set(),
                    postings=[
                        data.Posting(
                            account="Assets:Cash",
                            units=amount.Amount(D(net_amt), "USD"),
                            cost=None,
                            price=None,
                            flag=None,
                            meta=None,
                        ),
                        data.Posting(
                            account="Expenses:Stripe-Fees",
                            units=amount.Amount(D(fee_amt), "USD"),
                            cost=None,
                            price=None,
                            flag=None,
                            meta=None,
                        ),
                        data.Posting(
                            account="Income:Revenue",
                            units=amount.Amount(D(total_amount), "USD"),
                            cost=None,
                            price=None,
                            flag=None,
                            meta=None,
                        ),
                    ],
                )
                entries.append(txn)

        return entries


CONFIG = [StripeImporter]
