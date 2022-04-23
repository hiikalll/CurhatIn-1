import datetime
from email import message
from functools import wraps
# from pyexpat.errors import messages


from flask import Flask, render_template, request, redirect, url_for, flash, session
from peewee import *
from hashlib import md5


app = Flask(__name__)
app.secret_key = 'secretkeyuye'

DATABASE = 'curhatdb2.db'
                         
database = SqliteDatabase(DATABASE)
# database = MySQLDatabase(DATABASE)

class BaseModel(Model):
    class Meta:
        database = database
        
        
class User(BaseModel):
    username = CharField(unique=True)
    password = CharField()
    email = CharField(unique=True)
    join_at = DateTimeField(default=datetime.datetime.now())
    
    
    def following(self):
        return User.select().join(
            Relationship, on=Relationship.to_user).where(
                Relationship.from_user == self).order_by(User.username)
            
    def followers(self):
        return User.select().join(
            Relationship, on=Relationship.from_user).where(
                Relationship.to_user == self).order_by(User.username)
            
            
    def is_following(self, user):
        return Relationship.select().where(
            (Relationship.from_user == self) &
            (Relationship.to_user == user)).exists()

class Message(BaseModel):
    user = ForeignKeyField(User, backref='messages')
    content = TextField()
    published_at = DateTimeField(default=datetime.datetime.now())
    
class Relationship(BaseModel):
    from_user = ForeignKeyField(User, backref='relationships')
    to_user = ForeignKeyField(User, backref='related_to')
    published_at = DateTimeField(default=datetime.datetime.now())
    
    class Meta:
        indexes = (
            (('from_user', 'to_user'), True),
        )
        

@app.before_request
def before_request():
    database.connect()
    
    
@app.after_request
def after_request(response):
    database.close()
    return response

def create_tables():
    database.create_tables([User, Relationship, Message])
    



# =======================
#  Routing
# ======================

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('logged_in'):
            return redirect(url_for('index', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

def redirect_if_logged(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('logged_in'):
            return redirect(url_for('home'))
        return f(*args, **kwargs)
    return decorated_function

    
def get_current_user():
    if session.get('logged_in'):
        return User.get(User.id == session['user_id'])
    
    
    
def auth_user(user):
    session['logged_in'] = True
    session['user_id'] = user.id
    session['username'] = user.username


@app.context_processor
def _inject_user():
    return {'active_user': get_current_user()}


def getUserOrAbort(username):
    try:
        return User.get(User.username == username)
        
    except User.DoesNotExist:
        return render_template('404.html')









# ==================
# routing


@app.route('/')
@redirect_if_logged
def index():
    return render_template('index.html')




@app.route('/home')
@login_required
def home():
    
    user = get_current_user()
    messages = (Message.select()
                .order_by(
                    Message.published_at.desc()))
    
    
    return render_template('home.html', messages = messages, user=user)
 
  
    

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST' and request.form['username'] and request.form['email'] and request.form['password']:
        try:
            with database.atomic():
                user = User.create(
                    username=request.form['username'],
                    password=md5(request.form['password'].encode('utf-8')).hexdigest(),
                    email=request.form['email'])

            
            return redirect(url_for('login'))
        
        except IntegrityError:
            flash('User already exists')
            return redirect(url_for('register'))
            
    return render_template('register.html')



@app.route('/login', methods=['GET', 'POST'])
@redirect_if_logged
def login():
    if request.method == 'POST' and request.form['username'] and request.form['password']:
        try:
            hashed_pass = md5(request.form['password'].encode('utf-8')).hexdigest()
            user = User.get(
                (User.username == request.form['username']) & 
                (User.get(User.password == hashed_pass)))
            
            
            
        except User.DoesNotExist:
            flash('Wrong user or password')
        
        else:
            auth_user(user)
            return redirect(url_for('home'))

        
    return render_template('login.html')



@app.route('/logout')
@login_required
def logout():
    session.clear()
    return redirect(url_for('index'))


# ==============
# routing to post


@app.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    user = get_current_user()
    if request.method == 'POST' and request.form['content']:
        message = Message.create(
            user = user,
            content = request.form['content']
            )
        
        flash('Message posted')
        return redirect(url_for('user_profile', username = user.username))
    
    return render_template('create.html')

@app.route('/edit', methods=['GET', 'POST'])
@login_required
def edit():
    user = get_current_user()
    if request.method == 'POST' and request.form['content'] and request.form['id']:
        message = Message.update(content = request.form['content']).where(Message.id == request.form['id']).execute()
        flash('Message posted')
        return redirect(url_for('user_profile', username = user.username))
    message = Message.select().where(Message.id == request.args.get('id')).first()
    return render_template('edit.html', message = message)

@app.route('/delete', methods=['GET'])
@login_required
def delete():
    message = Message.delete().where(Message.id == request.args.get('id')).execute()
    user = get_current_user()
    return redirect(url_for('user_profile', username = user.username))
    

@app.route('/user/<username>')
@login_required
def user_profile(username):
    user = getUserOrAbort(username)
    if(username == get_current_user().username):
        myself = True 
    else:
        myself = False
    email = user.email
    messages = Message.select().where(Message.user == user).order_by(Message.published_at.desc())
    return render_template('user.html', messages=messages, user=user, email=email, myself=myself)
        


# def usredirect(username):
#     user = User.get(User.username == username)
#     return redirect(url_for('user_profile', username=user.username))

@app.route('/404')
def not_found():
    return render_template('404.html')
    
    


@app.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == 'POST' and request.form['search']:
        search_term = request.form['search']
        messages = Message.select().where(Message.content.contains(search_term))
        return render_template('search.html', messages=messages, search_term=search_term)
    
    return render_template('search.html')


@app.route('/about')
def about():
    return render_template('about.html')


# follow and unfollow
@app.route('/follow/<username>', methods=['POST'])
def follow_user(username):
    try:
        user = User.get(User.username == username)
        
    except User.DoesNotExist:
        return render_template('404.html')
    
    
    try:
        with database.atomic():
            Relationship.create(
                from_user=get_current_user(),
                to_user = user)
            
    except IntegrityError:
        pass
    
    flash('You are now following ' + username)
    return redirect(url_for('user_profile', username=username))


@app.route('/unfollow/<username>', methods=['POST'])
def unfollow_user(username):
    user = getUserOrAbort(username)
    

    (Relationship.delete().where(
        (Relationship.from_user == get_current_user()) &
        (Relationship.to_user == user)).execute())
            
        
    flash('You are no longer following ' + username)
    return redirect(url_for('user_profile', username=username))



@app.route('/user/<username>/followers')
def show_followers(username):
    user = getUserOrAbort(username)
    
    followers = user.followers()
    return render_template('followers.html', users = followers, user = user)


@app.route('/user/<username>/following')
def show_following(username):
    user = getUserOrAbort(username)
    
    return render_template('following.html', users = user.following(), user = user)

