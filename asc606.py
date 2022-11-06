import argparse
import datetime
from dateutil.relativedelta import relativedelta
import random
import string
import sys

from beancount.core import number, flags, amount
from beancount.core.data import Transaction, Posting, new_metadata
from beancount.parser import printer


def increment_time(_date: datetime.date, _type: str = "monthly"):
    if _type == "monthly":
        return _date + relativedelta(months=1)
    if _type == "daily":
        return _date + datetime.timedelta(days=1)


def main():
    parser = argparse.ArgumentParser(description="Yeehaw")
    # parser.add_argument(
    #     "-i",
    #     "--input-format",
    #     default=False,  # => can also be a string
    #     help="",
    #     # action="store_true", =>  if you need a bool or int
    #     # dest="new_name_of_var", =>  to change its name
    # )
    parser.add_argument(
        "-a",
        "--amount",
        type=float,
        required=True,
        help="Total Amount to Go into cash at outset",
    )
    parser.add_argument(
        "-p",
        "--periods",
        required=True,
        type=int,
        help="Number of periods this will be spread out over",
    )
    parser.add_argument(
        "-d",
        "--deferred-revenue-account",
        default="Liabilities:Deferred-Revenue",
        help='Deferred Revenue Account. Defaults to "Liabilities:Deferred-Revenue"',
    )
    parser.add_argument(
        "-r",
        "--revenue-account",
        default="Revenue:Sales",
        help='Final Revenue Account. Defaults to "Revenue:Sales"',
    )
    parser.add_argument("-i", "--installment-space", default="monthly", help="")
    args = parser.parse_args()
    _date = datetime.datetime.today().date()
    link_str = "deferred-revenue-%s" % "".join(
        [random.choice(string.hexdigits) for _ in range(9)]
    )

    # Initial Transaction into Deferred Revenue
    txn = Transaction(
        meta=new_metadata("output.beancount", 0),
        date=_date,
        flag=flags.FLAG_OKAY,
        payee="payee",  # both payee and narration get mangled
        narration="What does this do?",
        tags={link_str},
        links={link_str},
        postings=[
            Posting(
                account="Assets:Cash",
                units=amount.Amount(number.D(args.amount), "USD"),
                cost=None,
                price=None,
                flag=None,
                meta=None,
            ),
            Posting(
                account=args.deferred_revenue_account,
                units=amount.Amount(number.D(-1 * args.amount), "USD"),
                cost=None,
                price=None,
                flag=None,
                meta=None,
            ),
        ],
    )

    printer.print_entry(txn)

    installment_amount = args.amount / args.periods

    for i in range(args.periods):
        txn = Transaction(
            meta=new_metadata("output.beancount", i + 1),
            date=_date,
            flag=flags.FLAG_OKAY,
            payee="",
            narration="What does this do?",
            tags={link_str},
            links={link_str},
            postings=[
                Posting(
                    account=args.deferred_revenue_account,
                    units=amount.Amount(number.D(installment_amount), "USD"),
                    cost=None,
                    price=None,
                    flag=None,
                    meta=None,
                ),
                Posting(
                    account=args.revenue_account,
                    units=amount.Amount(number.D(-1 * installment_amount), "USD"),
                    cost=None,
                    price=None,
                    flag=None,
                    meta=None,
                ),
            ],
        )
        printer.print_entry(txn)
        _date = increment_time(_date, "monthly")


if __name__ == "__main__":
    main()
