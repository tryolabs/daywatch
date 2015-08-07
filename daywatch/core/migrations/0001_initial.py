# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Language'
        db.create_table(u'core_language', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('code', self.gf('django.db.models.fields.CharField')(max_length=3)),
            ('name', self.gf('django.db.models.fields.TextField')(max_length=255)),
        ))
        db.send_create_signal(u'core', ['Language'])

        # Adding model 'Country'
        db.create_table(u'core_country', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=255)),
            ('timezone', self.gf('django.db.models.fields.CharField')(unique=True, max_length=100)),
            ('code', self.gf('django.db.models.fields.CharField')(unique=True, max_length=5)),
            ('lang', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['core.Language'])),
        ))
        db.send_create_signal(u'core', ['Country'])

        # Adding model 'Currency'
        db.create_table(u'core_currency', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('country', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['core.Country'], unique=True)),
            ('iso_code', self.gf('django.db.models.fields.CharField')(max_length=5)),
            ('us_change', self.gf('django.db.models.fields.FloatField')()),
            ('regex', self.gf('django.db.models.fields.CharField')(max_length=30, blank=True)),
            ('text', self.gf('django.db.models.fields.CharField')(max_length=10)),
        ))
        db.send_create_signal(u'core', ['Currency'])

        # Adding model 'UserProfile'
        db.create_table(u'core_userprofile', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['auth.User'], unique=True)),
            ('panel_access', self.gf('core.fields.MultiSelectField')(max_length=300, null=True, blank=True)),
        ))
        db.send_create_signal(u'core', ['UserProfile'])

        # Adding M2M table for field country_access on 'UserProfile'
        m2m_table_name = db.shorten_name(u'core_userprofile_country_access')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('userprofile', models.ForeignKey(orm[u'core.userprofile'], null=False)),
            ('country', models.ForeignKey(orm[u'core.country'], null=False))
        ))
        db.create_unique(m2m_table_name, ['userprofile_id', 'country_id'])

        # Adding model 'Category'
        db.create_table(u'core_category', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=200)),
        ))
        db.send_create_signal(u'core', ['Category'])

        # Adding model 'Site'
        db.create_table(u'core_site', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=255)),
            ('image_path', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('url', self.gf('django.db.models.fields.URLField')(max_length=200)),
            ('spider_name', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('spider_enabled', self.gf('django.db.models.fields.BooleanField')()),
            ('host_name', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('country', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['core.Country'])),
            ('shows_sold_count', self.gf('django.db.models.fields.BooleanField')(default=True)),
        ))
        db.send_create_signal(u'core', ['Site'])

        # Adding model 'Merchant'
        db.create_table(u'core_merchant', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('lat', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=10, decimal_places=7, blank=True)),
            ('lon', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=10, decimal_places=7, blank=True)),
            ('address', self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True)),
            ('phone', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('website', self.gf('django.db.models.fields.URLField')(max_length=500, null=True, blank=True)),
            ('email', self.gf('django.db.models.fields.EmailField')(max_length=254, null=True, blank=True)),
        ))
        db.send_create_signal(u'core', ['Merchant'])

        # Adding model 'Item'
        db.create_table(u'core_item', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('offer', self.gf('django.db.models.fields.TextField')(max_length=255, null=True)),
            ('url', self.gf('django.db.models.fields.URLField')(max_length=500, null=True)),
            ('hash_id', self.gf('django.db.models.fields.CharField')(max_length=500, null=True, db_index=True)),
            ('description', self.gf('django.db.models.fields.TextField')(max_length=5000, null=True)),
            ('raw_html', self.gf('django.db.models.fields.TextField')(null=True)),
            ('image_url', self.gf('django.db.models.fields.URLField')(max_length=200, null=True)),
            ('date_time', self.gf('django.db.models.fields.DateTimeField')(db_index=True)),
            ('category', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['core.Category'], null=True, blank=True)),
            ('currency', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['core.Currency'], null=True)),
            ('price', self.gf('django.db.models.fields.FloatField')(null=True)),
            ('discount', self.gf('django.db.models.fields.FloatField')(null=True)),
            ('sold_count', self.gf('django.db.models.fields.IntegerField')(null=True)),
            ('city', self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True)),
            ('end_date_time', self.gf('django.db.models.fields.DateTimeField')(null=True)),
            ('active', self.gf('django.db.models.fields.NullBooleanField')(null=True, blank=True)),
            ('site', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['core.Site'])),
            ('merchant', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['core.Merchant'])),
        ))
        db.send_create_signal(u'core', ['Item'])

        # Adding model 'BufferedItem'
        db.create_table(u'core_buffereditem', (
            (u'item_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['core.Item'], unique=True, primary_key=True)),
        ))
        db.send_create_signal(u'core', ['BufferedItem'])

        # Adding model 'TestItem'
        db.create_table(u'core_testitem', (
            (u'item_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['core.Item'], unique=True, primary_key=True)),
        ))
        db.send_create_signal(u'core', ['TestItem'])

        # Adding model 'ActivityLog'
        db.create_table(u'core_activitylog', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('user_agent', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('referer', self.gf('django.db.models.fields.TextField')(max_length=700, null=True)),
            ('query_path', self.gf('django.db.models.fields.CharField')(max_length=300, null=True)),
            ('absolute_uri', self.gf('django.db.models.fields.TextField')(max_length=800, null=True)),
            ('date_time', self.gf('django.db.models.fields.DateTimeField')()),
        ))
        db.send_create_signal(u'core', ['ActivityLog'])

        # Adding model 'ErrorLog'
        db.create_table(u'core_errorlog', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('site', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['core.Site'])),
            ('date_time', self.gf('django.db.models.fields.DateTimeField')()),
            ('exception_name', self.gf('django.db.models.fields.CharField')(max_length=30, null=True)),
            ('exception_message', self.gf('django.db.models.fields.TextField')(max_length=200, null=True)),
            ('category', self.gf('django.db.models.fields.TextField')(max_length=50, null=True)),
            ('exception_trace', self.gf('django.db.models.fields.TextField')(max_length=200, null=True)),
            ('error_level', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal(u'core', ['ErrorLog'])

        # Adding model 'SoldCount'
        db.create_table(u'core_soldcount', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('deal', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['core.Item'])),
            ('date', self.gf('django.db.models.fields.DateTimeField')()),
            ('value', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal(u'core', ['SoldCount'])

        # Adding model 'Run'
        db.create_table(u'core_run', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('site', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['core.Site'])),
            ('start', self.gf('django.db.models.fields.DateTimeField')()),
            ('end', self.gf('django.db.models.fields.DateTimeField')(null=True)),
            ('scraped', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal(u'core', ['Run'])


    def backwards(self, orm):
        # Deleting model 'Language'
        db.delete_table(u'core_language')

        # Deleting model 'Country'
        db.delete_table(u'core_country')

        # Deleting model 'Currency'
        db.delete_table(u'core_currency')

        # Deleting model 'UserProfile'
        db.delete_table(u'core_userprofile')

        # Removing M2M table for field country_access on 'UserProfile'
        db.delete_table(db.shorten_name(u'core_userprofile_country_access'))

        # Deleting model 'Category'
        db.delete_table(u'core_category')

        # Deleting model 'Site'
        db.delete_table(u'core_site')

        # Deleting model 'Merchant'
        db.delete_table(u'core_merchant')

        # Deleting model 'Item'
        db.delete_table(u'core_item')

        # Deleting model 'BufferedItem'
        db.delete_table(u'core_buffereditem')

        # Deleting model 'TestItem'
        db.delete_table(u'core_testitem')

        # Deleting model 'ActivityLog'
        db.delete_table(u'core_activitylog')

        # Deleting model 'ErrorLog'
        db.delete_table(u'core_errorlog')

        # Deleting model 'SoldCount'
        db.delete_table(u'core_soldcount')

        # Deleting model 'Run'
        db.delete_table(u'core_run')


    models = {
        u'auth.group': {
            'Meta': {'object_name': 'Group'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        u'auth.permission': {
            'Meta': {'ordering': "(u'content_type__app_label', u'content_type__model', u'codename')", 'unique_together': "((u'content_type', u'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Group']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Permission']"}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'core.activitylog': {
            'Meta': {'object_name': 'ActivityLog'},
            'absolute_uri': ('django.db.models.fields.TextField', [], {'max_length': '800', 'null': 'True'}),
            'date_time': ('django.db.models.fields.DateTimeField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'query_path': ('django.db.models.fields.CharField', [], {'max_length': '300', 'null': 'True'}),
            'referer': ('django.db.models.fields.TextField', [], {'max_length': '700', 'null': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"}),
            'user_agent': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        u'core.buffereditem': {
            'Meta': {'object_name': 'BufferedItem', '_ormbases': [u'core.Item']},
            u'item_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['core.Item']", 'unique': 'True', 'primary_key': 'True'})
        },
        u'core.category': {
            'Meta': {'object_name': 'Category'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        u'core.country': {
            'Meta': {'object_name': 'Country'},
            'code': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '5'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'lang': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['core.Language']"}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
            'timezone': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100'})
        },
        u'core.currency': {
            'Meta': {'object_name': 'Currency'},
            'country': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['core.Country']", 'unique': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'iso_code': ('django.db.models.fields.CharField', [], {'max_length': '5'}),
            'regex': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'text': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'us_change': ('django.db.models.fields.FloatField', [], {})
        },
        u'core.errorlog': {
            'Meta': {'object_name': 'ErrorLog'},
            'category': ('django.db.models.fields.TextField', [], {'max_length': '50', 'null': 'True'}),
            'date_time': ('django.db.models.fields.DateTimeField', [], {}),
            'error_level': ('django.db.models.fields.IntegerField', [], {}),
            'exception_message': ('django.db.models.fields.TextField', [], {'max_length': '200', 'null': 'True'}),
            'exception_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'null': 'True'}),
            'exception_trace': ('django.db.models.fields.TextField', [], {'max_length': '200', 'null': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'site': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['core.Site']"})
        },
        u'core.item': {
            'Meta': {'object_name': 'Item'},
            'active': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'category': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['core.Category']", 'null': 'True', 'blank': 'True'}),
            'city': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'currency': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['core.Currency']", 'null': 'True'}),
            'date_time': ('django.db.models.fields.DateTimeField', [], {'db_index': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'max_length': '5000', 'null': 'True'}),
            'discount': ('django.db.models.fields.FloatField', [], {'null': 'True'}),
            'end_date_time': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'hash_id': ('django.db.models.fields.CharField', [], {'max_length': '500', 'null': 'True', 'db_index': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image_url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'null': 'True'}),
            'merchant': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['core.Merchant']"}),
            'offer': ('django.db.models.fields.TextField', [], {'max_length': '255', 'null': 'True'}),
            'price': ('django.db.models.fields.FloatField', [], {'null': 'True'}),
            'raw_html': ('django.db.models.fields.TextField', [], {'null': 'True'}),
            'site': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['core.Site']"}),
            'sold_count': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '500', 'null': 'True'})
        },
        u'core.language': {
            'Meta': {'object_name': 'Language'},
            'code': ('django.db.models.fields.CharField', [], {'max_length': '3'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.TextField', [], {'max_length': '255'})
        },
        u'core.merchant': {
            'Meta': {'object_name': 'Merchant'},
            'address': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '254', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'lat': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '10', 'decimal_places': '7', 'blank': 'True'}),
            'lon': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '10', 'decimal_places': '7', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'phone': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'website': ('django.db.models.fields.URLField', [], {'max_length': '500', 'null': 'True', 'blank': 'True'})
        },
        u'core.run': {
            'Meta': {'object_name': 'Run'},
            'end': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'scraped': ('django.db.models.fields.IntegerField', [], {}),
            'site': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['core.Site']"}),
            'start': ('django.db.models.fields.DateTimeField', [], {})
        },
        u'core.site': {
            'Meta': {'object_name': 'Site'},
            'country': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['core.Country']"}),
            'host_name': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image_path': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
            'shows_sold_count': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'spider_enabled': ('django.db.models.fields.BooleanField', [], {}),
            'spider_name': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '200'})
        },
        u'core.soldcount': {
            'Meta': {'object_name': 'SoldCount'},
            'date': ('django.db.models.fields.DateTimeField', [], {}),
            'deal': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['core.Item']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'value': ('django.db.models.fields.IntegerField', [], {})
        },
        u'core.testitem': {
            'Meta': {'object_name': 'TestItem', '_ormbases': [u'core.Item']},
            u'item_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['core.Item']", 'unique': 'True', 'primary_key': 'True'})
        },
        u'core.userprofile': {
            'Meta': {'object_name': 'UserProfile'},
            'country_access': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['core.Country']", 'symmetrical': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'panel_access': ('core.fields.MultiSelectField', [], {'max_length': '300', 'null': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['auth.User']", 'unique': 'True'})
        }
    }

    complete_apps = ['core']