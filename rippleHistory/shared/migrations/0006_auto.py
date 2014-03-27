# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting field 'Transaction.final_balance'
        db.delete_column(u'shared_transaction', 'final_balance')

        # Adding field 'Transaction.transaction_fee'
        db.add_column(u'shared_transaction', 'transaction_fee',
                      self.gf('django.db.models.fields.BigIntegerField')(default=0),
                      keep_default=False)


    def backwards(self, orm):

        # User chose to not deal with backwards NULL issues for 'Transaction.final_balance'
        raise RuntimeError("Cannot reverse this migration. 'Transaction.final_balance' and its values cannot be restored.")
        
        # The following code is provided here to aid in writing a correct migration        # Adding field 'Transaction.final_balance'
        db.add_column(u'shared_transaction', 'final_balance',
                      self.gf('django.db.models.fields.BigIntegerField')(),
                      keep_default=False)

        # Deleting field 'Transaction.transaction_fee'
        db.delete_column(u'shared_transaction', 'transaction_fee')


    models = {
        u'shared.account': {
            'Meta': {'object_name': 'Account'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ripple_address': ('django.db.models.fields.TextField', [], {'unique': 'True', 'db_index': 'True'})
        },
        u'shared.balance': {
            'Meta': {'object_name': 'Balance'},
            'account': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['shared.Account']"}),
            'balance': ('django.db.models.fields.BigIntegerField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ledger': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['shared.Ledger']"})
        },
        u'shared.ledger': {
            'Meta': {'object_name': 'Ledger'},
            'close_time': ('django.db.models.fields.DateTimeField', [], {}),
            'got_transactions': ('django.db.models.fields.BooleanField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ledger_hash': ('django.db.models.fields.TextField', [], {'unique': 'True', 'db_index': 'True'}),
            'parent_hash': ('django.db.models.fields.TextField', [], {'null': 'True'})
        },
        u'shared.transaction': {
            'Meta': {'object_name': 'Transaction'},
            'amount_currency': ('django.db.models.fields.TextField', [], {}),
            'amount_issuer': ('django.db.models.fields.TextField', [], {}),
            'amount_value': ('django.db.models.fields.TextField', [], {}),
            'from_account': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'from_account'", 'to': u"orm['shared.Account']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ledger': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['shared.Ledger']"}),
            'to_account': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'to_account'", 'to': u"orm['shared.Account']"}),
            'transaction_fee': ('django.db.models.fields.BigIntegerField', [], {})
        }
    }

    complete_apps = ['shared']