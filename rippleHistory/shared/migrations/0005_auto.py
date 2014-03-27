# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'Ledger.got_transactions'
        db.add_column(u'shared_ledger', 'got_transactions',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'Ledger.got_transactions'
        db.delete_column(u'shared_ledger', 'got_transactions')


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
            'final_balance': ('django.db.models.fields.BigIntegerField', [], {}),
            'from_account': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'from_account'", 'to': u"orm['shared.Account']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ledger': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['shared.Ledger']"}),
            'to_account': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'to_account'", 'to': u"orm['shared.Account']"})
        }
    }

    complete_apps = ['shared']