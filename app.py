from flask import Flask, url_for
from flask_admin import Admin
from config import SECRET_KEY, SQLALCHEMY_DATABASE_URI, INPUT_STAGING_AREA, OUTPUT_STAGING_AREA
from utils import queryresult_to_dict
from flask_sqlalchemy import SQLAlchemy
from flask_security import Security, SQLAlchemyUserDatastore, \
    UserMixin, RoleMixin, login_required, roles_required, current_user, utils
from flask_admin import helpers as admin_helpers
from flask_admin.contrib import sqla
from flask import Flask, url_for, redirect, request, abort
from wtforms import StringField, PasswordField
from flask_login import current_user
from flask_security.forms import RegisterForm
from sqlalchemy.sql import text
from flask import jsonify
import uuid
from flask_admin.contrib.sqla import ModelView
import os
import saga_utils
from flask import send_from_directory
from apscheduler.schedulers.background import BackgroundScheduler
from saga_utils import stage_output_files, cleanup_directory
from werkzeug.utils import secure_filename
import ast

# role definitions
SUPERUSER_ROLE = 'superuser'
POWERUSER_ROLE = 'poweruser'


scheduler = BackgroundScheduler()


app = Flask(__name__, static_url_path='/home/ubuntu/PycharmProjects/hemelb-hoff/static')
app.config.from_pyfile('config.py')


admin = Admin(app, name='Hoff', template_mode='bootstrap3')

# add database connection
app.config['SECRET_KEY'] = SECRET_KEY
app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI
db = SQLAlchemy(app)


# Define models
roles_users = db.Table(
    'roles_users',
    db.Column('user_id', db.Integer(), db.ForeignKey('user.id')),
    db.Column('role_id', db.Integer(), db.ForeignKey('role.id'))
)


class Role(db.Model, RoleMixin):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))

    def __str__(self):
        return self.name


class User(UserMixin, db.Model):
    def __repr__(self):
        return self.first_name + " " + self.last_name

    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(255))
    last_name = db.Column(db.String(255))
    email = db.Column(db.String(255), unique=True)
    password = db.Column(db.String(255))
    active = db.Column(db.Boolean())
    confirmed_at = db.Column(db.DateTime())
    roles = db.relationship('Role', secondary=roles_users,
                            backref=db.backref('users', lazy='dynamic'))


# quick model for testing jobs
class JobModel(db.Model):

    __tablename__ = 'JOB'

    id = db.Column(db.Integer(), primary_key=True)
    local_job_id = db.Column(db.String(80), unique=True)
    name = db.Column(db.String(80))
    executable = db.Column(db.String(255))
    state = db.Column(db.String(80))
    num_total_cpus = db.Column(db.Integer())
    total_physical_memory = db.Column(db.String(80))
    wallclock_limit = db.Column(db.String(80))
    project = db.Column(db.String(80))
    queue = db.Column(db.String(80))



    def __repr__(self):
        return self.name

# Setup Flask-Security
user_datastore = SQLAlchemyUserDatastore(db, User, Role)

class ExtendedRegisterForm(RegisterForm):
    first_name = StringField('First Name')
    last_name = StringField('Last Name')

security = Security(app, user_datastore, register_form=ExtendedRegisterForm)

# define a context processor for merging flask-admin's template context into the
# flask-security views.
@security.context_processor
def security_context_processor():
    return dict(
        admin_base_template=admin.base_template,
        admin_view=admin.index_view,
        h=admin_helpers,
        get_url=url_for
    )

# Create customized model view class
class UserModelView(sqla.ModelView):

    column_list = ('first_name', 'last_name', 'email')
    column_searchable_list = ('first_name', 'last_name', 'email')
    column_exclude_list = ('password')
    form_excluded_columns = ('password')

    can_create = True
    can_delete = False

    def is_accessible(self):
        if not current_user.is_active or not current_user.is_authenticated:
            return False
        if current_user.has_role('superuser'):
            return True
        return False

    def _handle_view(self, name, **kwargs):
        if not self.is_accessible():
            if current_user.is_authenticated:
                # permission denied
                abort(403)
            else:
                # login
                return redirect(url_for('security.login', next=request.url))

                # On the form for creating or editing a User, don't display a field corresponding to the model's password field.
                # There are two reasons for this. First, we want to encrypt the password before storing in the database. Second,
                # we want to use a password field (with the input masked) rather than a regular text field.

    def scaffold_form(self):

        # Start with the standard form as provided by Flask-Admin. We've already told Flask-Admin to exclude the
        # password field from this form.
        form_class = super(UserModelView, self).scaffold_form()

        # Add a password field, naming it "password2" and labeling it "New Password".
        form_class.password2 = PasswordField('New Password')
        return form_class

        # This callback executes when the user saves changes to a newly-created or edited User -- before the changes are
        # committed to the database.

    def on_model_change(self, form, model, is_created):

        # If the password field isn't blank...
        if len(model.password2):
            # ... then encrypt the new password prior to storing it in the database. If the password field is blank,
            # the existing password in the database will be retained.
            # TODO - put a password strength checker here?
            model.password = utils.hash_password(model.password2)


class RoleModelView(sqla.ModelView):

        def is_accessible(self):
            if not current_user.is_active or not current_user.is_authenticated:
                return False
            if current_user.has_role('superuser'):
                return True
            return False

        def _handle_view(self, name, **kwargs):
            if not self.is_accessible():
                if current_user.is_authenticated:
                    # permission denied
                    abort(403)
                else:
                    # login
                    return redirect(url_for('security.login', next=request.url))






# Add administrative views here
admin.add_view(RoleModelView(Role, db.session))
admin.add_view(UserModelView(User, db.session))
admin.add_view(ModelView(JobModel, db.session))


# rest endpoint definitions
@app.route('/jobs')
@login_required
def list_jobs():
    # normal users can only see their own jobs
    # super users and power users can see all jobs
    result = None
    if current_user.has_roles(SUPERUSER_ROLE) or current_user.has_role(POWERUSER_ROLE):
        cmd = 'SELECT local_job_id, name, state FROM JOB ORDER BY created'
        result = db.engine.execute(text(cmd))
    else:
        cmd = 'SELECT local_job_id, name, state FROM JOB WHERE user_id = :user_id'
        result = db.engine.execute(text(cmd), user_id=current_user.get_id())
    return jsonify(queryresult_to_dict({'local_job_id','name','state'}, result))

@app.route('/jobs',  methods=['POST'])
@login_required
def create_new_job():
    # look for json job description in payload

    payload = request.json

    # name, service, and executable are mandatory,
    # otherwise the job is pointless

    job_name = payload['name']
    service_name = payload['service']
    executable = payload['executable']

    # look for additional information, will set as NULL if not in payload
    arguments = payload.get('arguments')
    num_total_cpus = payload.get('num_total_cpus')
    total_physical_memory = payload.get('total_physical_memory')
    wallclock_limit = payload.get('wallclock_limit')
    project = payload.get('project')
    queue = payload.get('queue')

    # sanity check env - must be able to turn it into a dict
    env = payload.get('env')
    if env is not None:
        try:
            sanitized_env = ast.literal_eval(env)
        except Exception as e:
            abort(500, "Cannot convert env to a dict")


    job_uuid = str(uuid.uuid4())

    # look up the service name to get the correct id
    cmd = 'SELECT id FROM SERVICE where name=:name'
    result = db.engine.execute(text(cmd), name=service_name)
    service_id = result.fetchone()['id']
    print service_id

    user_id = current_user.get_id()

    cmd = 'INSERT INTO JOB(user_id, name, executable, service_id, local_job_id, arguments, env, num_total_cpus, total_physical_memory, wallclock_limit, project, queue) \
        VALUES(:user_id, :name, :executable, :service_id, :local_job_id, :arguments, :env, :num_total_cpus, :total_physical_memory, :wallclock_limit, :project, :queue )'
    db.engine.execute(text(cmd), user_id=user_id, name=job_name, executable=executable, service_id=service_id, local_job_id=job_uuid,
                      arguments=arguments, env=env, num_total_cpus=num_total_cpus, total_physical_memory=total_physical_memory,
                      wallclock_limit=wallclock_limit, project=project, queue=queue)

    # create a staging area for this job
    os.mkdir(os.path.join(INPUT_STAGING_AREA, job_uuid))


    return str(job_uuid)

@app.route('/job/<id>/state',  methods=['GET'])
@login_required
def get_job_state(id):
    # normal users can only see information about jobs they own
    # power and superusers can see everything
    cmd = "SELECT state, user_id FROM JOB WHERE local_job_id=:local_job_id"
    result = db.engine.execute(text(cmd), local_job_id = id).fetchone()
    state = result['state']
    owner = result['user_id']

    if int(owner) != int(current_user.get_id()):
        if not (current_user.has_role(POWERUSER_ROLE) or current_user.has_role(SUPERUSER_ROLE)):
            abort(403)

    return jsonify(state)


@app.route('/job/<id>',  methods=['GET'])
@login_required
def get_job_description(id):
    # normal users can only see information about jobs they own
    # power and superusers can see everything

    cmd = "SELECT * FROM JOB WHERE local_job_id=:local_job_id"
    result = db.engine.execute(text(cmd), local_job_id = id)
    job_record = result.fetchone()

    if int(job_record['user_id']) != int(current_user.get_id()):
        if not (current_user.has_role(POWERUSER_ROLE) or current_user.has_role(SUPERUSER_ROLE)):
            abort(403)


    jd = {}
    jd["name"] = job_record['name']
    jd["executable"] = job_record['executable']
    jd["service_id"] = job_record['service_id']
    jd["local_job_id"] = job_record["local_job_id"]
    jd["remote_job_id"] = job_record["remote_job_id"]
    jd["arguments"] = job_record['arguments']
    jd["env"] = job_record['env']
    jd["num_total_cpus"] = job_record["num_total_cpus"]
    jd["total_physical_memory"] = job_record['total_physical_memory']
    jd["wallclock_limit"] = job_record['wallclock_limit']
    jd["project"] = job_record["project"]
    jd["queue"] = job_record["queue"]
    return jsonify(jd)


@app.route('/jobs/<id>/submit',  methods=['POST'])
@login_required
def submit_job(id):

    # only the owner of a job can submit it

    cmd = "SELECT * FROM JOB WHERE local_job_id=:local_job_id"
    result = db.engine.execute(text(cmd), local_job_id=id).fetchone()

    if(int(result['user_id']) != int(current_user.get_id())):
        abort(403)

    if result['state'] != "NEW":
        abort("inconsistent state", 500)
    jd = {}
    jd['local_job_id'] = result['local_job_id']
    jd['name'] = result['name']
    jd['service_id'] = result['service_id']
    jd['executable'] = result['executable']

    # look for additional information, will set as NULL if not in payload
    jd['arguments'] = result['arguments']
    jd['num_total_cpus'] = result['num_total_cpus']
    jd['total_physical_memory'] = result['total_physical_memory']
    jd['wallclock_limit'] = result['wallclock_limit']
    jd['project'] = result['project']
    jd['queue'] = result['queue']

    # if env is specified, we need to turn the arguments into a dict
    if result['env'] is not None:
        try:
            jd['env'] = ast.literal_eval(result['env'])
        except Exception as e:
            abort(500, "couldn't convert env parameter to a dict")

    local_input_file_dir = os.path.join(INPUT_STAGING_AREA, jd['local_job_id'])

    service_id = result['service_id']
    service = get_service(service_id)

    saga_utils.stage_input_files(id, local_input_file_dir, service)

    remote_job_id = saga_utils.submit_saga_job(jd, service)

    if remote_job_id != -1:
        # update database
        cmd = "UPDATE JOB SET state=:state, remote_job_id=:remote_job_id WHERE local_job_id=:local_job_id"
        db.engine.execute(text(cmd), state="SUBMITTED", remote_job_id=remote_job_id, local_job_id=id)
        return 'Submitted', 200, {'Content-Type': 'text/plain'}
    else:
        abort(500, "error submitting job")


@app.route('/jobs/<id>/files',  methods=['POST'])
@login_required
def add_file_to_job(id):
    # first check the job exists
    cmd = "SELECT local_job_id, user_id FROM JOB WHERE local_job_id=:local_job_id"
    result = db.engine.execute(text(cmd), local_job_id=id)
    r = result.fetchone()
    if r is None:
        abort(404)
    local_job_id = r['local_job_id']
    user_id = r['user_id']
    if int(r['user_id']) != int(current_user.get_id()):
        abort(403)

    for f in request.files:
        file = request.files[f]
        file.save(os.path.join(INPUT_STAGING_AREA, local_job_id, secure_filename(f)))

    return 'Success', 200, {'Content-Type': 'text/plain'}

@app.route('/jobs/<id>/files',  methods=['GET'])
@login_required
def get_job_output_file_list(id):

    # quickly check if the job id is real
    cmd = "SELECT local_job_id, user_id FROM JOB WHERE local_job_id=:local_job_id"
    result = db.engine.execute(text(cmd), local_job_id=id)
    r = result.fetchone()
    if r is None:
        abort(404)
    local_job_id = r['local_job_id']
    user_id = r['user_id']

    # normal users can only see their own jobs
    if int(user_id) != int(current_user.get_id()):
        if not ( current_user.has_role(SUPERUSER_ROLE) or current_user.has_role(POWERUSER_ROLE)):
            abort(403)

    # list the files in the job's output directory
    # in the case of Azure we would list the output storage container

    filelist = []
    base_dir = os.path.join(OUTPUT_STAGING_AREA, local_job_id)
    for path, subdirs, files in os.walk(base_dir):
        for name in files:
            filelist.append( os.path.join(path, name).replace(base_dir+"/",''))


    #dirlist = os.listdir(os.path.join(OUTPUT_STAGING_AREA, local_job_id))
    return jsonify(filelist)




@app.route('/jobs/<job_id>/files/<path:path>',  methods=['GET'])
@login_required
def get_job_output_file(job_id, path):

    # quickly check if the job id is real
    cmd = "SELECT local_job_id, user_id FROM JOB WHERE local_job_id=:local_job_id"
    result = db.engine.execute(text(cmd), local_job_id=job_id)
    r = result.fetchone()
    if r is None:
        abort(404)
    local_job_id = r['local_job_id']
    user_id = r['user_id']

    if int(user_id) != int(current_user.get_id()):
        abort(403)

    # check if the requested file exists
    # we need a check to see if we are listing normal files or redirecting to Azure - TODO


    exists = os.path.isfile(os.path.join(OUTPUT_STAGING_AREA, local_job_id, path))
    if not exists:
        abort(404)

    return send_from_directory(directory=os.path.join(OUTPUT_STAGING_AREA, local_job_id), filename=path)


@app.route('/jobs/<id>', methods=['DELETE'])
@login_required
def delete_job(id):
    return 'delete_job'

@app.route('/services', methods=['GET'])
@login_required
def list_resources():
    cmd = 'SELECT name, url FROM SERVICE'
    result = db.engine.execute(text(cmd))
    return jsonify(queryresult_to_dict({'name', 'url'}, result))

@app.route('/inputsets', methods=['POST'])
@login_required
def create_input_set():
    return 'create_input_set'

@app.route('/inputsets', methods=['GET'])
@login_required
def list_input_sets():
    return 'list_input_set'


@app.route('/test/<id>', methods=['GET'])
@login_required
def do_test(id):
    return submit_job(id)



# refresh the local job state for any jobs with a local state of SUBMITTED
# do this on some kind of background thread?
def refresh_job_state():

    try:

        cmd = "SELECT local_job_id, remote_job_id, service_id FROM JOB WHERE state='SUBMITTED'"
        result = db.engine.execute(text(cmd))
        for r in result:

            try:
                local_job_id = r['local_job_id']
                remote_job_id = r['remote_job_id']

                service = get_service(r['service_id'])
                remote_state = saga_utils.get_remote_job_state(remote_job_id, service)

                if (remote_state in ['Done', 'DONE', 'Failed', 'FAILED']):
                    # update the local state
                    cmd = "UPDATE JOB SET state=:state WHERE local_job_id=:local_job_id"
                    db.engine.execute(text(cmd), state=remote_state, local_job_id=local_job_id)

                    # add a job to retrieve any output files
                    scheduler.add_job(retrieve_output_files(local_job_id))
            except Exception as e:
                # TODO logging
                print e

    except Exception as e:
        # TODO logging
        print e


def get_service(service_id):
    cmd = "SELECT * FROM SERVICE WHERE id=:service_id"
    result = db.engine.execute(text(cmd), service_id=service_id).fetchone()

    service = {}
    service["name"] = result["name"]
    service["scheduler_url"] = result["scheduler_url"]
    service["username"] = result["username"]
    service["user_pass"] = result["user_pass"]
    service["user_key"] = result["user_key"]
    service["file_url"] = result["file_url"]
    service["working_directory"] = result["working_directory"]
    return service

def retrieve_output_files(job_id):
    cmd = "SELECT remote_job_id, service_id FROM JOB WHERE local_job_id=:local_job_id"
    result = db.engine.execute(text(cmd), local_job_id=job_id)
    job = result.fetchone()

    local_file_dir = os.path.join(OUTPUT_STAGING_AREA, job_id)

    service = get_service(job['service_id'])

    try:
        REMOTE_WORKING_DIR = os.path.join(service['working_directory'], str(job_id))
        stage_output_files(REMOTE_WORKING_DIR, local_file_dir, service)
        cleanup_directory(REMOTE_WORKING_DIR, service)
        # flag the job as retrieved
        cmd = "UPDATE JOB SET retrieved=1 WHERE local_job_id=:local_job_id"
        db.engine.execute(text(cmd), local_job_id=job_id)

    except Exception as e:
        # TODO log error somewhere
        print e



scheduler.add_job(refresh_job_state, 'interval', minutes=1)
scheduler.start()

app.run()