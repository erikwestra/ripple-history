""" rippleHistory.api.views

    This module defines the vaious views for the rippleHistory.api application.
"""
from django.http           import HttpResponse, HttpResponseNotAllowed
from django.http           import HttpResponseBadRequest, HttpResponseNotFound
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

import simplejson as json

from rippleHistory.shared.models import *

#############################################################################

def lookup(request, ripple_address):
    """ Respond to the "/lookup/<ripple_address>" URL.
    """
    # Start by finding the Account record with the given ripple address.

    try:
        account = Account.objects.get(ripple_address=ripple_address)
    except Account.DoesNotExist:
        return HttpResponse("No data found for that ripple address.")

    # Now get the balance records for this account.  Each balance record should
    # hold the balance for a given combination of currency and issuer.

    balances = []
    for balance in Balance.objects.filter(account=account):
        balances.append(balance)

    # Next, get the raw transaction records for this account.  Note that a
    # transaction may come from the account, or to to the account -- we have to
    # check each separately.

    transactions = []
    for transaction in Transaction.objects.filter(from_account=account):
        transactions.append(("out", transaction))
    for transaction in Transaction.objects.filter(to_account=account):
        transactions.append(("in", transaction))

    # Sort the transactions by the ledger close time.

    transactions.sort(key=lambda transaction: transaction[1].ledger.close_time)

    # Testing: simply dump the returned information so we can see what we have.

    html = []
    html.append('<html>')
    html.append('  <head>')
    html.append('    <title>Ripple History for ' + ripple_address + '</title>')
    html.append('    <style>')
    html.append('      td.heading {')
    html.append('        text-align: center;')
    html.append('        font-weight: bold;')
    html.append('        border-bottom: 1px solid black;')
    html.append('      }')
    html.append('    </style>')
    html.append('  </head>')
    html.append('  <body>')
    html.append('     <h2>Ripple Address</h2>')
    html.append('     <blockquote>')
    html.append('       ' + ripple_address)
    html.append('     </blockquote>')
    html.append('     <h2>Balances</h2>')
    html.append('     <blockquote>')
    html.append('       <table border="0" cellspacing="5" cellpadding="0">')
    html.append('         <tr>')
    html.append('           <td class="heading">')
    html.append('             Date/Time')
    html.append('           </td>')
    html.append('           <td class="heading">')
    html.append('             Currency')
    html.append('           </td>')
    html.append('           <td class="heading">')
    html.append('             Amount')
    html.append('           </td>')
    html.append('           <td class="heading">')
    html.append('             Issuer')
    html.append('           </td>')
    html.append('         </tr>')
    for balance in balances:
        html.append('         <tr>')
        html.append('           <td>')
        html.append('             ' + str(balance.ledger.close_time))
        html.append('           </td>')
        html.append('           <td>')
        html.append('             ' + balance.balance_currency)
        html.append('           </td>')
        html.append('           <td>')
        html.append('             ' + balance.balance_value)
        html.append('           </td>')
        html.append('           <td>')
        html.append('             ' + balance.balance_issuer)
        html.append('           </td>')
        html.append('         </tr>')
    html.append('       </table>')
    html.append('     </blockquote>')
    html.append('     <h2>Transactions</h2>')
    html.append('     <blockquote>')
    html.append('       <table border="0" cellspacing="5" cellpadding="0">')
    html.append('         <tr>')
    html.append('           <td class="heading">')
    html.append('             Date/Time')
    html.append('           </td>')
    html.append('           <td class="heading">')
    html.append('             Type')
    html.append('           </td>')
    html.append('           <td class="heading">')
    html.append('             Other Account')
    html.append('           </td>')
    html.append('           <td class="heading">')
    html.append('             Transaction Fee')
    html.append('           </td>')
    html.append('           <td class="heading">')
    html.append('             Currency')
    html.append('           </td>')
    html.append('           <td class="heading">')
    html.append('             Amount')
    html.append('           </td>')
    html.append('           <td class="heading">')
    html.append('             Issuer')
    html.append('           </td>')
    html.append('         </tr>')
    for direction,transaction in transactions:
        if direction == "out":
            other_account = transaction.to_account
        else:
            other_account = transaction.from_account

        html.append('         <tr>')
        html.append('           <td>')
        html.append('             ' + str(transaction.ledger.close_time))
        html.append('           </td>')
        html.append('           <td>')
        if direction == "out":
            html.append('             Withdrawal')
        else:
            html.append('             Deposit')
        html.append('           </td>')
        html.append('           <td>')
        html.append('             ' + other_account.ripple_address)
        html.append('           </td>')
        html.append('           <td>')
        html.append('             ' + str(transaction.transaction_fee))
        html.append('           </td>')
        html.append('           <td>')
        html.append('             ' + transaction.amount_currency)
        html.append('           </td>')
        html.append('           <td>')
        html.append('             ' + transaction.amount_value)
        html.append('           </td>')
        html.append('           <td>')
        html.append('             ' + transaction.amount_issuer)
        html.append('           </td>')
        html.append('         </tr>')
    html.append('       </table>')
    html.append('     </blockquote>')
    html.append('  </body>')
    html.append('</html>')
    return HttpResponse("\n".join(html))

#############################################################################

def get(request, ripple_address):
    """ Return the raw transaction and balance data in JSON format.
    """
    # Start by finding the Account record with the given ripple address.

    try:
        account = Account.objects.get(ripple_address=ripple_address)
    except Account.DoesNotExist:
        return HttpResponseNotFound()

    # Now get the balance records for this account.  Each balance record should
    # hold the balance for a given combination of currency and issuer.

    balances = []
    for balance in Balance.objects.filter(account=account):
        balances.append(balance)

    # Next, get the raw transaction records for this account.  Note that a
    # transaction may come from the account, or to to the account -- we have to
    # check each separately.

    transactions = []
    for transaction in Transaction.objects.filter(from_account=account):
        transactions.append(("out", transaction))
    for transaction in Transaction.objects.filter(to_account=account):
        transactions.append(("in", transaction))

    # Sort the transactions by the ledger close time.

    transactions.sort(key=lambda transaction: transaction[1].ledger.close_time)

    # Assemble the raw data to return.

    data = {}

    data['balances'] = []
    for balance in balances:
        timestamp = balance.ledger.close_time.isoformat()

        data['balances'].append({'timestamp' : timestamp,
                                 'currency'  : balance.balance_currency,
                                 'value'     : balance.balance_value,
                                 'issuer'    : balance.balance_issuer})

    data['transactions'] = []
    for direction,transaction in transactions:
        timestamp = transaction.ledger.close_time.isoformat()

        if direction == "out":
            type    = "withdrawal"
            account = transaction.to_account
        else:
            type    = "deposit"
            account = transaction.from_account

        data['transactions'].append({'timestamp' : timestamp,
                                     'type'      : type,
                                     'account'   : account.ripple_address,
                                     'fee'       : transaction.transaction_fee,
                                     'currency'  : transaction.amount_currency,
                                     'value'     : transaction.amount_value,
                                     'issuer'    : transaction.amount_issuer})

    # Finally, send the data back to the caller.

    return HttpResponse(json.dumps(data), content_type="application/json")

#############################################################################

def balances(request):
    """ Respond to the "/balances" endpoint.

        We return a list of all known account balances, filtered by currency.
    """
    # Get the request parameters.

    if request.method == "GET":
        params = request.GET
    elif request.method == "POST":
        params = request.POST
    else:
        return HttpResponseNotAllowed(["GET", "POST"])

    if "currency" not in params:
        return HttpResponseBadRequest("Missing required 'currency' parameter")
    currency = params['currency']

    if currency == "XRP":
        issuer = ""
    else:
        if "issuer" not in params:
            return HttpResponseBadRequest(
                            "Missing required 'issuer' parameter")
        issuer = params['issuer']

    # Get the desired page of account balances.

    all_balances = Balance.objects.filter(balance_currency=currency,
                                          balance_issuer=issuer)

    paginator = Paginator(all_balances, 10000) # 10,000 balances per page.
    page = params.get("page")

    try:
        balances = paginator.page(page)
    except PageNotAnInteger:
        balances = paginator.page(1)
    except EmptyPage:
        balances = []

    response = {}
    for balance in balances:
        response[balance.account.ripple_address] = balance.balance_value

    # Finally, send the data back to the caller.

    return HttpResponse(json.dumps(response), content_type="application/json")

