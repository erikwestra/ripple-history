""" rippleHistory.shared.management.commands.get_ledgers

    This Django management command runs continually, downloading ledger details
    from the "rippled" server.
"""
import datetime
import decimal
import os
import os.path

from optparse import make_option

from django.core.management.base import BaseCommand, CommandError
from django.conf                 import settings

import simplejson as json
import websocket

from rippleHistory.shared.models          import *
from rippleHistory.shared.lib.ledgerChain import LedgerChain

#############################################################################

class Command(BaseCommand):
    """ Our "get_ledgers" management command.
    """
    args        = None
    help        = "Download ledger details from the rippled server."
    option_list = BaseCommand.option_list + (
        make_option("--log-to-file",
                    action="store_true",
                    dest="log_to_file",
                    default=False,
                    help="Write log messages to a file on disk."),
    )


    def __init__(self):
        """ Standard initialiser.
        """
        self._log_to_file              = False # Save log messages to file?
        self._callbacks                = {}    # Maps request ID to callback.
        self._next_req_id              = 1     # Next request ID to use.
        self._socket                   = None  # Our open Websocket.
        self._latest_ledger_on_startup = None  # most recent Ledger object.
        self._known_accounts           = {}    # Maps Ripple address to rec ID.
        self._num_account_balances     = 0     # Number of retrieved balances.
        self._queued_account_balances  = []    # List of queued Balance recs.
        self._ledger_chain             = None  # Our LedgerChain object.

        BaseCommand.__init__(self)


    def handle(self, *args, **options):
        if len(args) != 0:
            raise CommandError("This command takes no parameters.")

        self._log_to_file = options['log_to_file']

        # Start by deleting all the existing account balances, and loading a
        # complete list of all known account IDs into memory.

        Balance.objects.all().delete()
        self._num_account_balances = 0

        self._known_accounts = {}
        for account in Account.objects.all():
            self._known_accounts[account.ripple_address] = account.id

        # Load the chain of ledgers into memory.

        self._ledger_chain = LedgerChain()
        for ledger in Ledger.objects.all():
            if ledger.got_transactions:
                self._ledger_chain.add(ledger.ledger_hash, ledger.parent_hash)

        # Finally, start up our websocket app.

        #websocket.enableTrace(True)
        websocket_url = settings.RIPPLED_SERVER_WEBSOCKET_URL
        self._socket = websocket.WebSocketApp(websocket_url,
                                              on_message=self.on_message,
                                              on_error=self.on_error,
                                              on_close=self.on_close)

        self._socket.on_open = self.on_open

        try:
            self._socket.run_forever()
        except KeyboardInterrupt:
            pass

    # =====================
    # == PRIVATE METHODS ==
    # =====================

    def send_request(self, command, params={}, callback=None):
        """ Send off a request to the rippled server.

            The parameters are as follows:

                'command'

                    The command to send to the server.

                'params'

                    A dictionary holding the parameters for this command, if
                    any.

                'callback'

                    A Python callable object, if any, to call when this command
                    is completed.  The callback will be called with a single
                    parameter, which will be the response returned by the
                    server.  Note that if 'callback' is set to None, no
                    callback will take place.
        """
        # Calculate a unique ID for this request.

        request_id = self._next_req_id
        self._next_req_id = self._next_req_id + 1

        # Remember the callback function to use for this request.

        self._callbacks[request_id] = callback

        # Send the request off to the server.

        request = {}
        request.update(params)
        request['command'] = command
        request['id'] = request_id

        self._socket.send(json.dumps(request))


    def on_open(self, ws):
        """ Respond to our websocket client starting up.

            We start by getting the hash of the most recently closed ledger,
            and then starting to process the ledger contents to get all the
            current account balances.  We also subscribe to the stream of
            "ledger close" events so that we can get the details for the new
            ledgers as they close.
        """
        self.log("Requesting latest ledger")
        self.send_request("ledger", {'ledger_index': "validated"},
                          callback=self.on_got_latest_ledger)


    def on_got_latest_ledger(self, response):
        """ Respond to use receiving the most recent ledger from the server.

            We ask the server to start sending us the ledger data for this
            ledger.
        """
        if response["status"] != "success":
            self.log("ERROR: ledger call returned %s" % str(response))
            return

        ledger_hash = response['result']['ledger']['ledger_hash']
        parent_hash = response['result']['ledger']['parent_hash']
        close_time  = response['result']['ledger']['close_time']

        try:
            ledger = Ledger.objects.get(ledger_hash=ledger_hash)
        except Ledger.DoesNotExist:
            ledger = Ledger()
            ledger.ledger_hash      = ledger_hash
            ledger.parent_hash      = parent_hash
            ledger.parent_id        = None
            ledger.close_time       = self.ripple_time_to_datetime(close_time)
            ledger.got_transactions = False
            ledger.save()

            self._ledger_chain.add(ledger_hash, parent_hash)

        self._latest_ledger_on_startup = ledger

        self.log("Requesting ledger data")
        self.send_request("ledger_data",
                          {"ledger_hash" : ledger_hash},
                          callback=self.on_got_ledger_data)


    def on_got_ledger_data(self, response):
        """ Respond to the server sending us a chunk of ledger data.

            We process the ledger data, updating the current balances for the
            accounts based on the returned data, and then either ask for more
            ledger data (if there is any), or start subscribing to ledger
            updates (if there isn't).
        """
        if response["status"] != "success":
            self.log("ERROR: ledger data call returned %s" % str(response))
            return

        for entry in response['result']['state']:
            if entry['LedgerEntryType'] == "AccountRoot":
                # We have an account balance in drops.  Convert it to XRP and
                # remember the balance.
                account = entry['Account']
                currency = "XRP"
                value    = str(decimal.Decimal(entry['Balance']) /
                               decimal.Decimal("1000000"))
                issuer   = ""
                self.remember_account_balance(account, currency, value, issuer)
            elif entry['LedgerEntryType'] == "RippleState":
                # We have an account IOU balance.  Remember it.
                account  = entry['LowLimit']['issuer']
                currency = entry['Balance']['currency']
                value    = entry['Balance']['value']
                issuer   = entry['HighLimit']['issuer']
                self.remember_account_balance(account, currency, value, issuer)

        if "marker" in response['result']:
            # We have more ledger data to come -> ask for it.
            self.log("Requesting more ledger data (%d balances so far)"
                     % self._num_account_balances)
            ledger_hash = self._latest_ledger_on_startup.ledger_hash
            self.send_request("ledger_data",
                              {"ledger_hash" : ledger_hash,
                               "marker"      : response['result']['marker']},
                              callback=self.on_got_ledger_data)
            return

        # If we get here, we've finished processing the ledger data.  Save any
        # remaining queued balances, and subscribe to the ledger close events
        # so we can get information on the transactions as they come in.

        if len(self._queued_account_balances) > 0:
            Balance.objects.bulk_create(self._queued_account_balances)
            self._queued_account_balances = []

        self.log("Received all %d account balances" %
                 self._num_account_balances)
        self.log("")
        self.log("Listening for ledger closed events...")

        self.send_request("subscribe",
                          {'streams' : ["ledger"]},
                          callback=None)


    def on_got_ledger(self, response):
        """ Respond to the server sending us the results of a "ledger" request.

            We process the transactions in the given ledger, and then check to
            see if we are missing any earlier ledgers.  If so, we re-issue the
            request for the missing ledger.
        """
        if response["status"] != "success":
            self.log("ERROR: ledger data call returned %s" % str(response))
            return

        ledger_hash = response['result']['ledger']['ledger_hash']
        parent_hash = response['result']['ledger']['parent_hash']
        close_time  = response['result']['ledger']['close_time']

        # Get the Ledger object for this ledger, creating it if necessary.

        try:
            ledger = Ledger.objects.get(ledger_hash=ledger_hash)
        except Ledger.DoesNotExist:
            ledger = Ledger()
            ledger.ledger_hash      = ledger_hash
            ledger.parent_hash      = parent_hash
            ledger.parent_id        = None
            ledger.close_time       = self.ripple_time_to_datetime(close_time)
            ledger.got_transactions = False
            ledger.save()

            self._ledger_chain.add(ledger_hash, parent_hash)

        self.log("Got ledger %s (%s)" % (ledger.ledger_hash,
                                         str(ledger.close_time)))

        # See if we already have the transactions for this ledger.  If not, add
        # them.

        if not ledger.got_transactions:

            transactions = []

            for trans in response['result']['ledger']['transactions']:
                if trans['TransactionType'] != "Payment":
                    # Ignore non-payment transactions.
                    continue

                # Extract the transaction details we need.

                src_account_hash = trans['Account']
                dst_account_hash = trans['Destination']
                transaction_fee  = long(trans['Fee']) # in "drops".

                if isinstance(trans['Amount'], basestring):
                    # The amount is in XRP.
                    amount_currency = "XRP"
                    amount_value    = trans['Amount']
                    amount_issuer   = ""
                else:
                    # The amount is in a foreign currency.
                    amount_currency = trans['Amount']['currency']
                    amount_value    = trans['Amount']['value']
                    amount_issuer   = trans['Amount']['issuer']

                # Get the source and destination accounts, creating them if
                # necessary.

                try:
                    src_account = Account.objects.get(
                                            ripple_address=src_account_hash)
                except Account.DoesNotExist:
                    src_account = Account()
                    src_account.ripple_address = src_account_hash
                    src_account.save()

                try:
                    dst_account = Account.objects.get(
                                            ripple_address=dst_account_hash)
                except Account.DoesNotExist:
                    dst_account = Account()
                    dst_account.ripple_address = dst_account_hash
                    dst_account.save()

                # Create a Transaction object for this transaction.

                transaction = Transaction()
                transaction.ledger          = ledger
                transaction.from_account    = src_account
                transaction.to_account      = dst_account
                transaction.transaction_fee = transaction_fee
                transaction.amount_currency = amount_currency
                transaction.amount_value    = amount_value
                transaction.amount_issuer   = amount_issuer

                transactions.append(transaction)

            # Save the transactions, and remember that we've done this.

            self.log("  -> Saving %d transactions for this ledger." %
                    len(transactions))

            Transaction.objects.bulk_create(transactions)

            ledger.got_transactions = True
            ledger.save()

        # See if we have the parent ledger, and its transactions.  If not,
        # request it.

        try:
            parent_ledger = Ledger.objects.get(ledger_hash=parent_hash)
        except Ledger.DoesNotExist:
            self.send_request("ledger",
                              {"ledger_hash"  : parent_hash,
                               "transactions" : True,
                               "expand"       : True},
                              callback=self.on_got_ledger)
            return

        if not parent_ledger.got_transactions:
            # We know about the parent ledger, but not the transactions within
            # it -> request it.
            self.send_request("ledger",
                              {"ledger_hash"  : parent_hash,
                               "transactions" : True,
                               "expand"       : True},
                              callback=self.on_got_ledger)
            return

        # If we get here, we have the parent ledger.  This means we have all
        # transactions from the parent ledger forward.  However, there might be
        # earlier ledgers that we don't yet have.  Look backwards through the
        # ledger chain to find the latest ledger we don't have transactions
        # for.

        chains = self._ledger_chain.get_chains()
        if len(chains) > 0:
            parent_hash = chains[-1]['first_parent']
            if parent_hash != "0": # Genesis ledger.
                self.send_request("ledger",
                                  {"ledger_hash"  : parent_hash,
                                   "transactions" : True,
                                   "expand"       : True},
                                  callback=self.on_got_ledger)


    def on_close(self, ws):
        """ Respond to the websocket connection being closed.
        """
        self.log("### Websocket connection closing ###")


    def on_message(self, ws, message):
        """ Respond to a message being received from the server.
        """
        response = json.loads(message)
        if response['type'] == "response":
            # We've got a response to a previous request -> pass it onto the
            # associated callback.
            request_id = response['id']

            try:
                callback = self._callbacks[request_id]
            except KeyError:
                self.log("!!! Missing callback for request ID %s" %
                         str(request_id))
                return

            del self._callbacks[request_id]

            if callback != None:
                callback(response)

            return

        # If we get here, we have a message initiated by the server.  We handle
        # these specially.

        if response['type'] == "ledgerClosed":
            # We've been notified that a ledger has closed.  Ask for the ledger
            # details.
            self.send_request("ledger",
                              {"ledger_hash"  : response['ledger_hash'],
                               "transactions" : True,
                               "expand"       : True},
                              callback=self.on_got_ledger)
            return

        # If we get here, we don't know what the message is -> display it to
        # the user.

        self.log("Unknown message received from server:")
        self.log("")
        self.log(message)


    def on_error(self, ws, error):
        """ Respond to a websocket error.
        """
        self.log("### error: %s ###" % str(error))


    def remember_account_balance(self, ripple_address, currency, value,
                                 issuer):
        """ Remember the given account balance.
        """
        if ripple_address not in self._known_accounts:
            # We haven't seen this account before -> create it.
            account = Account()
            account.ripple_address = ripple_address
            account.save()
            self._known_accounts[ripple_address] = account.id

        balance = Balance()
        balance.ledger           = self._latest_ledger_on_startup
        balance.account_id       = self._known_accounts[ripple_address]
        balance.balance_currency = currency
        balance.balance_value    = value
        balance.balance_issuer   = issuer

        self._queued_account_balances.append(balance)

        if len(self._queued_account_balances) > 1000:
            Balance.objects.bulk_create(self._queued_account_balances)
            self._queued_account_balances = []

        self._num_account_balances = self._num_account_balances + 1


    def ripple_time_to_datetime(self, close_time):
        """ Convert the given "ripple time" value to a Datetime object.
        """
        timestamp = long(close_time) + 946684800
        return datetime.datetime.fromtimestamp(timestamp)


    def log(self, msg):
        """ Write the given message to our log.
        """
        if self._log_to_file:
            log_dir = os.path.join(settings.ROOT_DIR, "temp")
            if not os.path.exists(log_dir):
                os.mkdir(log_dir)
            f = file(os.path.join(log_dir, "worker.log"), "a")
            f.write(msg + "\n")
            f.close()
        else:
            self.stdout.write(msg + "\n")

