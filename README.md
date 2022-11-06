# Scripts for Processing Ledger


## Stripe Importer

Beancount _sucks_ at reports but being its in Python you can write and
manipulate importers much more easily. Therefore, its useful to write
to beancount and then dump to hledger compatible.  

This uses the "all transactions" CSV which is different than the "all
payments" CSV. The former can be found `Payments > All Payments > All
Transactions > Export`.  

The importer is meant to be modified. It serves as a jumping off
point. For instance, you probably want the transaction id, charge
source (`ch_`) and description to be on one line.  

For determining more complex revenue recognition (e.g. ASC606), you
could use the STATEMENT DESCRIPTOR in the payments CSV. But then
you'll lose the transactions API which looks more complete (could be
wrong). Presumably you could ballpark on price from there. But as you
grow, it probably makes more sense to use the [invoice id against the
Stripe API](https://stripe.com/docs/api/invoices/line_item). Keep in
mind that [Stripe's default limit for reads is
~100/sec](https://stripe.com/docs/rate-limits) so you'd presumably
need to keep that in check.  


## Columns in Stripe File

```
id,Type,Source,Amount,Fee,Destination Platform Fee,Destination Platform Fee Currency,Net,Currency,Created (UTC),Available On (UTC),Description,Customer Facing Amount,Customer Facing Currency,Transfer,Transfer Date (UTC),Transfer Group
txn_XYZ,charge,ch_XYZ,30.00,1.17,,,28.83,usd,2022-04-23 21:56,2022-04-30 00:00,Invoice XYZXYZXY-dddd,30.00,usd,,,
```



## ASC606 

```
$ python asc606.py --amount 10000 --periods 9

2022-11-06 * "my new payee" "my new description" #deferred-revenue-B5a44C05a ^deferred-revenue-B5a44C05a
  Assets:Cash                    1200 USD
  Liabilities:Deferred-Revenue  -1200 USD

2022-11-06 * "my new payee" "my new description" #deferred-revenue-B5a44C05a ^deferred-revenue-B5a44C05a
  Liabilities:Deferred-Revenue   200 USD
  Revenue:Sales                 -200 USD

2022-12-06 * "my new payee" "my new description" #deferred-revenue-B5a44C05a ^deferred-revenue-B5a44C05a
  Liabilities:Deferred-Revenue   200 USD
  Revenue:Sales                 -200 USD

2023-01-06 * "my new payee" "my new description" #deferred-revenue-B5a44C05a ^deferred-revenue-B5a44C05a
  Liabilities:Deferred-Revenue   200 USD
  Revenue:Sales                 -200 USD

2023-02-06 * "my new payee" "my new description" #deferred-revenue-B5a44C05a ^deferred-revenue-B5a44C05a
  Liabilities:Deferred-Revenue   200 USD
  Revenue:Sales                 -200 USD

2023-03-06 * "my new payee" "my new description" #deferred-revenue-B5a44C05a ^deferred-revenue-B5a44C05a
  Liabilities:Deferred-Revenue   200 USD
  Revenue:Sales                 -200 USD

2023-04-06 * "my new payee" "my new description" #deferred-revenue-B5a44C05a ^deferred-revenue-B5a44C05a
  Liabilities:Deferred-Revenue   200 USD
  Revenue:Sales                 -200 USD
```
