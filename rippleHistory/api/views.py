""" rippleHistory.api.views

    This module defines the vaious views for the rippleHistory.api application.
"""
from django.http import HttpResponse

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

###########

    for direction,transaction in transactions:
        if direction == "out":
            other_account = transaction.to_account
        else:
            other_account = transaction.from_account

        html.append("   " + direction +
                 "   " + other_account.ripple_address +
                 "   " + transaction.transation_fee +
                 "   " + transaction.amount_currency +
                 "   " + transaction.amount_value +
                 "   " + transaction.amount_issuer)

    return HttpResponse("<p/>".join(html))



