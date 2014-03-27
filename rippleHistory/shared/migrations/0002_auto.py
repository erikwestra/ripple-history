# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Balance'
        db.create_table(u'shared_balance', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('ledger', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['shared.Ledger'])),
            ('account', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['shared.Account'])),
            ('balance', self.gf('django.db.models.fields.BigIntegerField')()),
        ))
        db.send_create_signal(u'shared', ['Balance'])

        # Adding model 'Ledger'
        db.create_table(u'shared_ledger', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('ledger_hash', self.gf('django.db.models.fields.TextField')(unique=True, db_index=True)),
            ('parent_hash', self.gf('django.db.models.fields.TextField')()),
            ('parent_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['shared.Ledger'])),
            ('close_time', self.gf('django.db.models.fields.DateTimeField')()),
        ))
        db.send_create_signal(u'shared', ['Ledger'])

        # Adding model 'Account'
        db.create_table(u'shared_account', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('ripple_address', self.gf('django.db.models.fields.TextField')(unique=True, db_index=True)),
        ))
        db.send_create_signal(u'shared', ['Account'])

        # Adding model 'Transaction'
        db.create_table(u'shared_transaction', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('ledger', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['shared.Ledger'])),
            ('from_account', self.gf('django.db.models.fields.related.ForeignKey')(related_name='from_account', to=orm['shared.Account'])),
            ('to_account', self.gf('django.db.models.fields.related.ForeignKey')(related_name='to_account', to=orm['shared.Account'])),
            ('amount_currency', self.gf('django.db.models.fields.TextField')()),
            ('amount_value', self.gf('django.db.models.fields.TextField')()),
            ('amount_issuer', self.gf('django.db.models.fields.TextField')()),
            ('final_balance', self.gf('django.db.models.fields.BigIntegerField')()),
        ))
        db.send_create_signal(u'shared', ['Transaction'])


    def backwards(self, orm):
        # Deleting model 'Balance'
        db.delete_table(u'shared_balance')

        # Deleting model 'Ledger'
        db.delete_table(u'shared_ledger')

        # Deleting model 'Account'
        db.delete_table(u'shared_account')

        # Deleting model 'Transaction'
        db.delete_table(u'shared_transaction')


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
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ledger_hash': ('django.db.models.fields.TextField', [], {'unique': 'True', 'db_index': 'True'}),
            'parent_hash': ('django.db.models.fields.TextField', [], {}),
            'parent_id': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['shared.Ledger']"})
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