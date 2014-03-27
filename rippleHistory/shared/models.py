""" rippleHistory.shared.models

    This file contains the Django models used by the rippleHistory system.
"""
from django.db import models

#############################################################################

class Ledger(models.Model):
    """ A single closed ledger within the Ripple system.

        Note that the "parent_hash" field contains the ledger hash of the
        parent (previous) ledger.  This forms a linked-list of ledgers going
        back in time.
    """
    id               = models.AutoField(primary_key=True)
    ledger_hash      = models.TextField(db_index=True, unique=True)
    parent_hash      = models.TextField(null=True)
    close_time       = models.DateTimeField()
    got_transactions = models.BooleanField()

#############################################################################

class Account(models.Model):
    """ A ripple account.
    """
    id             = models.AutoField(primary_key=True)
    ripple_address = models.TextField(db_index=True, unique=True)

#############################################################################

class Balance(models.Model):
    """ A current balance within an account.

        Note that we only keep one current balance for each account -- when
        loading a new set of ledger data, we replace the old balances with the
        new ones.
    """
    ledger           = models.ForeignKey(Ledger)
    account          = models.ForeignKey(Account)
    balance_currency = models.TextField()
    balance_value    = models.TextField() # ???
    balance_issuer   = models.TextField()

#############################################################################

class Transaction(models.Model):
    """ A transaction against a single Ripple account.
    """
    ledger          = models.ForeignKey(Ledger)
    from_account    = models.ForeignKey(Account, related_name="from_account")
    to_account      = models.ForeignKey(Account, related_name="to_account")
    transaction_fee = models.BigIntegerField()
    amount_currency = models.TextField()
    amount_value    = models.TextField() # ???
    amount_issuer   = models.TextField()

