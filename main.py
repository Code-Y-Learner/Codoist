from flask import Flask, render_template, redirect, url_for, flash, abort, request, jsonify
from flask_bootstrap import Bootstrap
from flask_ckeditor import CKEditor
import datetime
import string, random, sys, os
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
from forms import LoginForm, RegisterForm, ModifyCompleteForm, ModifyDeadlineForm, AddForm, DateForm
from flask_wtf import FlaskForm, CSRFProtect


app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get("SECRET_KEY")
Bootstrap(app)
# enable CSRF protection
app.config['CKEDITOR_ENABLE_CSRF'] = True
csrf = CSRFProtect(app)

##CONNECT TO DB
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///user_db.db" # os.environ.get("DATABASE_URL") #
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


##CONFIGURE TABLE
class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    name = db.Column(db.String(100))
    code = db.Column(db.String(100))
    todo = relationship("TodoList", back_populates="author")
    timers = relationship("Timer", back_populates="usercode")


class TodoList(db.Model):
    __tablename__ = "todolists"
    id = db.Column(db.Integer, primary_key=True)
    author_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    author = relationship("User", back_populates="todo")
    title = db.Column(db.String(250), unique=True, nullable=False)
    date = db.Column(db.String(250), nullable=False)
    deadline = db.Column(db.String(250), nullable=True)
    priority = db.Column(db.Text, nullable=True)
    # img_url = db.Column(db.String(250), nullable=False)
    timers = relationship("Timer", back_populates="parent_todolist")
    complete = db.Column(db.String(100), nullable=False)


class Timer(db.Model):
    __tablename__ = "timers"
    id = db.Column(db.Integer, primary_key=True)
    todolist_id = db.Column(db.Integer, db.ForeignKey('todolists.id'))
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    usercode = relationship("User", back_populates="timers")
    parent_todolist = relationship("TodoList", back_populates="timers")
    time = db.Column(db.DATETIME, server_default=db.func.now())
    status = db.Column(db.String(100), nullable=False)


# db.drop_all()
db.create_all()

def admin_only(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.id != 1:
            return abort(403)
        return f(*args, **kwargs)

    return decorated_function


@app.route('/')
def home():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return render_template("index.html", current_user=current_user)

# @app.route('/pomodoro/', methods=["GET", "POST"])
# @login_required
# def pomodoro():
#     standard_date = datetime.today()
#     form_date = DateForm()
#
#     if form_date.validate_on_submit():
#     return render_template('pomodoro.html',current_user = current_user)


@app.route('/dashboard/', methods=["GET", "POST"])
@login_required
def dashboard():
    form_complete = ModifyCompleteForm()
    form_deadline = ModifyDeadlineForm()
    form_add = AddForm()
    if form_complete.validate_on_submit():
        if (form_complete.complete1.data or form_complete.complete2.data or form_complete.complete3.data):
            print('form1')
            for i in range(1, 4):
                if getattr(form_complete, f"complete{i}").data:
                    title = form_complete.title.data
                    user_code = form_complete.usercode.data
                    todolist_to_modify = TodoList.query.filter_by(title=title, author=User.query.filter_by(
                        code=user_code).first()).first()
                    complete = str(getattr(form_complete, f"complete{i}")).split('value="')[1].split('"')[0]
                    todolist_to_modify.complete = complete
                    db.session.commit()
        if (form_deadline.submit2.data or form_deadline.daily.data):
            print('form2')
            if form_deadline.daily.data:
                print(form_deadline.daily.data)
                title = form_complete.title.data
                user_code = form_complete.usercode.data
                todolist_to_modify = TodoList.query.filter_by(title=title, author=User.query.filter_by(
                    code=user_code).first()).first()
                todolist_to_modify.deadline = ''
                db.session.commit()
            elif form_deadline.submit2.data:
                deadline = form_deadline.deadline.data.strftime('%Y/%m/%d')
                title = form_complete.title.data
                user_code = form_complete.usercode.data
                todolist_to_modify = TodoList.query.filter_by(title=title, author=User.query.filter_by(
                    code=user_code).first()).first()
                todolist_to_modify.deadline = deadline
                db.session.commit()
    if form_add.submit3.data:
        if User.query.filter_by(code=current_user.code).first():
            if TodoList.query.filter_by(title=form_add.title.data,
                                        author=User.query.filter_by(code=current_user.code).first()).first():
                flash("This todolist already exists.")
                return redirect(url_for('dashboard'))
            else:
                if form_add.deadline.data == None:
                    deadline = ''
                else:
                    deadline = form_add.deadline.data.strftime('%Y/%m/%d')
                new_todolist = TodoList(
                    author=User.query.filter_by(code=current_user.code).first(),
                    date=datetime.datetime.today().strftime("%Y-%m-%d"),
                    title=form_add.title.data,
                    deadline=deadline,
                    complete=form_add.complete.data,
                )
                db.session.add(new_todolist)
                db.session.commit()
                return redirect(url_for('dashboard'))
    def check_length():
        todolist_daily = 0
        todolist_deadline = 0
        cardlength_daily = [3,6]
        cardlength_deadline = [3,6]
        for todolist  in current_user.todo:
            if todolist.deadline == '':
                todolist_daily += 1
            else:
                todolist_deadline += 1
        if todolist_daily >= 3:
            cardlength_daily = [2,6]
        if todolist_deadline >= 3:
            cardlength_deadline = [2,6]
        return cardlength_daily, cardlength_deadline

    def check_progress():
        count_deadline = 0
        count_daily = 0
        count_notdone_deadline = 0
        count_notdone_daily =0
        deadline_over = 0
        progress_deadline = 0
        progress_daily = 0
        for todolist  in current_user.todo:
            # deadline todolist 점검
            if todolist.deadline != '':
                if todolist.complete != 'O':
                    count_notdone_deadline += 1
                if datetime.datetime.strptime(todolist.deadline, '%Y/%m/%d') < datetime.datetime.today():
                    if todolist.complete != 'O':
                        deadline_over += 1

                count_deadline += 1

            # daily todolist 점검
            else:
                if todolist.complete != 'O':
                    count_notdone_daily += 1
                count_daily += 1
            if count_daily == 0:
                progress_daily = 0
            else:
                progress_daily = round((count_daily-count_notdone_daily)*100/count_daily,1)
            if count_deadline ==0:
                progress_deadline = 0
            else:
                progress_deadline = round((count_deadline-count_notdone_deadline)*100/count_deadline,1)
        return [ deadline_over, progress_deadline , progress_daily ]

    progress = check_progress()
    cardlength_daily, cardlength_deadline = check_length()

    return render_template("dashboard.html", current_user=current_user, form_1=form_deadline, form_2=form_complete,
                           form_3=form_add, length_daily = cardlength_daily, length_deadline = cardlength_deadline, progress = progress )


@app.route("/delete/<int:todolist_id>")
@login_required
def delete_todolist(todolist_id):
    todolist_to_delete = TodoList.query.get(todolist_id)
    db.session.delete(todolist_to_delete)
    db.session.commit()
    return redirect(url_for('dashboard'))


@app.route('/pomodoro/', methods=["GET", "POST"])
def get_pomodoro_data():
    if request.method == "GET":
        user_code = request.args.get("usercode")
        title = request.args.get("title")
        if User.query.filter_by(code=user_code).first():
            new_time = Timer(
                parent_todolist=TodoList.query.filter_by(title=title,
                                     author=User.query.filter_by(code=user_code).first()).first(),
                usercode=User.query.filter_by(code=user_code).first(),
                time=datetime.datetime.strptime(request.args.get('date'), "%Y-%m-%d %H:%M:%S.%f"),
                status=request.args.get("status"),
            )
            db.session.add(new_time)
            db.session.commit()
            return jsonify(response={"success": "Successfully added."})
        else:
            return jsonify(response={'Failed': "Unvalid usercode"})


@app.route('/todolist/', methods=["GET", "POST"])
def get_todolist_data():
    if request.method == "GET":
        user_code = request.args.get("usercode")
        print(User.query.filter_by(code=user_code).first())
        if User.query.filter_by(code=user_code).first():
            if TodoList.query.filter_by(title=request.args.get("title"),
                                        author=User.query.filter_by(code=user_code).first()).first():
                return jsonify(response={"Failed": "Already uploaded"})
            else:
                new_todolist = TodoList(
                    author=User.query.filter_by(code=user_code).first(),
                    date=request.args.get('date'),
                    title=request.args.get("title"),
                    deadline=request.args.get('deadline'),
                    complete=request.args.get("complete"),
                )
                db.session.add(new_todolist)
                db.session.commit()
                return jsonify(response={"success": "Successfully added ."})
        else:
            return jsonify(response={'Failed': "Unvalid usercode"})


@app.route('/todolist/modify/<title>', methods=["GET", "POST"])
def modify_todolist_data(title):
    if request.method == "GET":
        user_code = request.args.get("usercode")
        if User.query.filter_by(code=user_code).first():
            todolist_to_modify = TodoList.query.filter_by(title=title,
                                                          author=User.query.filter_by(code=user_code).first()).first()
            if todolist_to_modify:
                print(todolist_to_modify.title)
                todolist_to_modify.title = title
                if request.args.get('date'):
                    todolist_to_modify.date = request.args.get('date')
                if request.args.get('deadline'):
                    todolist_to_modify.deadline = request.args.get('deadline')
                if request.args.get('complete'):
                    todolist_to_modify.complete = request.args.get('complete')
                db.session.commit()
                return jsonify(response={"Success": "Delete complete."})
            else:
                return jsonify(response={"Failed": "Anvalid todolist."})
        else:
            return jsonify(response={'Failed': "Unvalid usercode"})


@app.route('/todolist/del/', methods=["GET", "POST"])
def del_todolist_data():
    if request.method == "GET":
        print(request.args.get('title'))
        user_code = request.args.get("usercode")
        if User.query.filter_by(code=user_code).first():
            todolist_to_del = TodoList.query.filter_by(title=request.args.get('title'),
                                                       author=User.query.filter_by(code=user_code).first()).first()
            if todolist_to_del:
                db.session.delete(todolist_to_del)
                db.session.commit()
                return jsonify(response={"Success": "Delete complete."})
            else:
                return jsonify(response={"Failed": "Anvalid todolist."})
        else:
            return jsonify(response={'Failed': "Unvalid usercode"})


@app.route('/todolist/call-mylist/', methods=["GET", "POST"])
def load_data():
    if request.method == "GET":
        user_code = request.args.get("usercode")
        post_datas = TodoList.query.filter_by(author=User.query.filter_by(code=user_code).first()).all()
        if post_datas:
            data = {}
            for i in range(0, len(post_datas)):
                data[i] = {
                    "title": post_datas[i].title,
                    "date": post_datas[i].date,
                    "complete": post_datas[i].complete,
                    "deadline": post_datas[i].deadline,
                }
            return jsonify(data)
        else:
            print("No data")


@app.route('/register', methods=["GET", "POST"])
def register():
    form = RegisterForm()

    def generate_usercode():
        letters = string.ascii_letters
        numbers = string.digits
        symbols = string.punctuation

        nr_letters = random.randint(3, 5)
        nr_numbers = random.randint(1, 3)
        nr_symbols = 1
        password_list = []

        password_letters = [random.choice(letters) for _ in range(nr_letters)]
        password_symbols = [random.choice(symbols) for _ in range(nr_symbols)]
        password_numbers = [random.choice(numbers) for _ in range(nr_numbers)]
        password_list = password_numbers + password_letters + password_symbols

        random.shuffle(password_list)

        usercode = "".join(password_list)
        return usercode

    if form.validate_on_submit():
        if User.query.filter_by(email=form.email.data).first():
            print(User.query.filter_by(email=form.email.data).first())
            # User already exists
            flash("You've already signed up with that email, log in instead!")
            return redirect(url_for('login'))

        hash_and_salted_password = generate_password_hash(
            form.password.data,
            method='pbkdf2:sha256',
            salt_length=8
        )
        user_code =  generate_usercode()
        new_user = User(
            email=form.email.data,
            name=form.name.data,
            password=hash_and_salted_password,
            code=user_code
        )
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user)
        return redirect(url_for("dashboard"))

    return render_template("register.html", form=form, current_user=current_user)


@app.route('/login', methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data

        user = User.query.filter_by(email=email).first()
        # Email doesn't exist or password incorrect.
        if not user:
            flash("That email does not exist, please try again.")
            return redirect(url_for('login'))
        elif not check_password_hash(user.password, password):
            flash('Password incorrect, please try again.')
            return redirect(url_for('login'))
        else:
            login_user(user)
            return redirect(url_for('dashboard'))
    return render_template("login.html", form=form, current_user=current_user)


#
#
@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route('/myai/')
def ai():
    my_id = "Code-Y-Learner"
    my_project = "First_project"
    # user_id = "stabilityai"
    # user_project = "stable-diffusion"
    url_src = f"https://hf.space/embed/{my_id}/{my_project}/+"
    return render_template("ai.html",src=url_src)


if __name__ == "__main__":
    app.run(host="0.0.0.0",port="8000")
