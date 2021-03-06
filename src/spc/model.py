from gluino import DAL, Field
import config

#db = DAL(config.uri, auto_import=True, migrate=False, folder=config.dbdir)
#db = DAL(config.uri, migrate=True, migrate_enabled=True, fake_migrate=True, folder=config.dbdir)
db = DAL(config.uri, migrate=False, folder=config.dbdir)

groups =  db.define_table('groups', Field('id', 'integer'),
                                    Field('name', 'string'))

users = db.define_table('users', Field('id', 'integer'),
                                 Field('user', 'string'),
                                 Field('passwd', 'string'),
                                 Field('email', 'string'),
                                 Field('new_shared_jobs', 'integer'),
                                 Field('priority', 'integer'),
                                 Field('gid', db.groups, ondelete="SET NULL"))

user_meta = db.define_table('user_meta', Field('id', 'integer'),
                                         Field('uid', db.users),
                                         Field('new_shared_jobs', 'integer'),
                                         Field('theme', 'string'))

# this is also defined in scheduler.py
# need to fix in the future
apps = db.define_table('apps', Field('id', 'integer'),
                               Field('name', 'string'),
                               Field('description', 'string'),
                               Field('category', 'string'),
                               Field('language', 'string'),
                               Field('input_format', 'string'),
                               Field('command', 'string'),
                               Field('assets', 'string'),
                               Field('preprocess', 'string'),
                               Field('postprocess', 'string'))

app_user = db.define_table('app_user', Field('id', 'integer'),
                                       Field('appid', 'integer'),
                                       Field('uid', 'integer'))

jobs = db.define_table('jobs', Field('id', 'integer'),
                               Field('uid', db.users),
                               Field('app', 'string'),
                               Field('cid', 'string'),
                               Field('gid', db.groups),
                               Field('command', 'string'),
                               Field('state', 'string'),
                               Field('time_submit', 'string'),
                               Field('walltime', 'string'),
                               Field('description', 'string'),
                               Field('np', 'integer'),
                               Field('priority', 'integer'),
                               Field('starred', 'string'),
                               Field('shared', 'string'))

plots = db.define_table('plots', Field('id', 'integer'),
                                 # need to turn on unique in the future, but will cause migration probs for old DBs
                                 # this is needed for running "spc update" b/c primary keys are not specified in spc.json
                                 Field('appid', db.apps), #unique=True),
                                 Field('ptype', 'string'),
                                 Field('title', 'string'),
                                 Field('options', 'string'))

datasource = db.define_table('datasource', Field('id', 'integer'),
                                           Field('label', 'string'), # unique=True),
                                           Field('pltid', db.plots),
                                           Field('filename', 'string'),
                                           Field('cols', 'string'),
                                           Field('line_range', 'string'),
                                           Field('data_def', 'string'))

aws_creds = db.define_table('aws_creds', Field('id', 'integer'),
                                         Field('key', 'string'),
                                         Field('secret', 'string'),
                                         Field('account_id', 'string'),
                                         Field('uid', db.users))

aws_instances = db.define_table('aws_instances', Field('id', 'integer'),
                                                 Field('region', 'string'),
                                                 Field('instance', 'string'),
                                                 Field('itype', 'string'),
                                                 Field('rate', 'double'),
                                                 Field('uid', db.users))
