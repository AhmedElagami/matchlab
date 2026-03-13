from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('matching', '0004_add_match_models'),
    ]

    operations = [
        # Mentor: remove dropped fields
        migrations.RemoveField(model_name='mentorprofile', name='coaching_topics'),
        migrations.RemoveField(model_name='mentorprofile', name='languages'),
        migrations.RemoveField(model_name='mentorprofile', name='location'),
        # Mentee: rename notes → bio (preserves data)
        migrations.RenameField(model_name='menteeprofile', old_name='notes', new_name='bio'),
        # Mentee: add new fields
        migrations.AddField(model_name='menteeprofile', name='job_title', field=models.CharField(blank=True, max_length=200)),
        migrations.AddField(model_name='menteeprofile', name='function', field=models.CharField(blank=True, max_length=200)),
        migrations.AddField(model_name='menteeprofile', name='years_experience', field=models.IntegerField(blank=True, null=True)),
    ]
