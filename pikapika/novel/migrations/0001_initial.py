# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Novel'
        db.create_table('novel_novel', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=512)),
            ('cat_code', self.gf('django.db.models.fields.CharField')(max_length=5)),
            ('description', self.gf('django.db.models.fields.TextField')()),
            ('author', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('publisher', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('image', self.gf('django.db.models.fields.files.ImageField')(max_length=100, blank=True)),
            ('rating_points', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('rating_count', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('updated_date', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
        ))
        db.send_create_signal('novel', ['Novel'])

        # Adding model 'Volume'
        db.create_table('novel_volume', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=512)),
            ('novel', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['novel.Novel'])),
            ('description', self.gf('django.db.models.fields.TextField')()),
            ('image', self.gf('django.db.models.fields.files.ImageField')(max_length=100, blank=True)),
            ('rating_points', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('rating_count', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('_order', self.gf('django.db.models.fields.IntegerField')(default=0)),
        ))
        db.send_create_signal('novel', ['Volume'])

        # Adding model 'Chapter'
        db.create_table('novel_chapter', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=512)),
            ('volume', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['novel.Volume'])),
            ('rating_points', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('rating_count', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('updated_date', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('posted_by', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('_order', self.gf('django.db.models.fields.IntegerField')(default=0)),
        ))
        db.send_create_signal('novel', ['Chapter'])

        # Adding model 'ChapterContent'
        db.create_table('novel_chaptercontent', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('chapter', self.gf('django.db.models.fields.related.OneToOneField')(related_name=u'content_record', unique=True, to=orm['novel.Chapter'])),
            ('content', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal('novel', ['ChapterContent'])


    def backwards(self, orm):
        # Deleting model 'Novel'
        db.delete_table('novel_novel')

        # Deleting model 'Volume'
        db.delete_table('novel_volume')

        # Deleting model 'Chapter'
        db.delete_table('novel_chapter')

        # Deleting model 'ChapterContent'
        db.delete_table('novel_chaptercontent')


    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'hitcount.hitcount': {
            'Meta': {'ordering': "('-hits',)", 'unique_together': "(('content_type', 'object_pk'),)", 'object_name': 'HitCount', 'db_table': "'hitcount_hit_count'"},
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'content_type_set_for_hitcount'", 'to': "orm['contenttypes.ContentType']"}),
            'hits': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'object_pk': ('django.db.models.fields.IntegerField', [], {})
        },
        'novel.chapter': {
            'Meta': {'ordering': "('_order',)", 'object_name': 'Chapter'},
            '_order': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '512'}),
            'posted_by': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"}),
            'rating_count': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'rating_points': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'updated_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'volume': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['novel.Volume']"})
        },
        'novel.chaptercontent': {
            'Meta': {'object_name': 'ChapterContent'},
            'chapter': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "u'content_record'", 'unique': 'True', 'to': "orm['novel.Chapter']"}),
            'content': ('django.db.models.fields.TextField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'novel.novel': {
            'Meta': {'ordering': "[u'-updated_date', u'-pk']", 'object_name': 'Novel'},
            'author': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'cat_code': ('django.db.models.fields.CharField', [], {'max_length': '5'}),
            'description': ('django.db.models.fields.TextField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '512'}),
            'publisher': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'rating_count': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'rating_points': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'updated_date': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        },
        'novel.volume': {
            'Meta': {'ordering': "('_order',)", 'object_name': 'Volume'},
            '_order': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'description': ('django.db.models.fields.TextField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '512'}),
            'novel': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['novel.Novel']"}),
            'rating_count': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'rating_points': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        }
    }

    complete_apps = ['novel']