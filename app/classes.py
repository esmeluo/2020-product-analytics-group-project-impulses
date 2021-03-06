"""
SQLAlchemy Object Relational Mapper (ORM) and Flask-WTForms

Including:
Classes for each table in the database -
user, plaid_items, accounts, transaction, savings_history, habits,
coin, lottery, and user_lottery_log

WTForms -
RegistrationForm, LogInForm, and HabitForm
"""

import pytz
from flask_login import UserMixin
from flask_wtf import FlaskForm

from werkzeug.security import check_password_hash, generate_password_hash
from wtforms import PasswordField, StringField, SubmitField, SelectField
from wtforms.validators import DataRequired, Length
from flask_migrate import Migrate
from datetime import datetime

from app import db, login_manager, application

migrate = Migrate(application, db)
TZ = pytz.timezone("America/Los_Angeles")


class User(db.Model, UserMixin):
    """Data model for user table.

    Columns include:
    user_id: auto increment primary key; int
    first_name: user's first name; string
    last_name: user's last name; string
    email: user's email address; string; unique
    phone: user's phone number; string; unique
    password_hash: user's hashed password; string
    signup_date: user's signup date; datetime
    status: user's current status; string
    auth_id: unique user id from OAuth if available; string
    coins: total number of coins the user has; int
    saving_suggestions: number of habit notifications sent to the user; int
    """
    __tablename__ = "user"
    id = db.Column("user_id", db.Integer, primary_key=True)
    first_name = db.Column(db.String, nullable=False)
    last_name = db.Column(db.String, nullable=False)
    email = db.Column(db.String, unique=True, nullable=False)
    phone = db.Column(db.String(10), unique=True, nullable=False)
    password_hash = db.Column(db.String, nullable=False)
    signup_date = db.Column(db.DateTime, nullable=False,
                            default=datetime.now().astimezone(TZ))
    status = db.Column(db.String, nullable=False, default="unverified")
    auth_id = db.Column(db.String, default=None)
    coins = db.Column(db.Integer, nullable=False, default=0)
    saving_suggestions = db.Column(db.Integer, nullable=False, default=0)

    # relationships
    plaid_items = db.relationship("PlaidItems", backref="user")
    accounts = db.relationship("Accounts", backref="user")
    transaction = db.relationship("Transaction", backref="user")
    savings_history = db.relationship("SavingsHistory", backref="user")
    habits = db.relationship("Habits", backref="user")
    coin = db.relationship("Coin", backref="user")
    lottery_log = db.relationship("UserLotteryLog", backref="user")

    def __init__(self, first_name, last_name, email,
                 phone, password, auth_id=None):
        """Initializes User class"""
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.phone = phone
        self.auth_id = auth_id
        self.set_password(password)

    def set_password(self, password):
        """Generates a hashed password"""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Check if the input password matches the actual password"""
        return check_password_hash(self.password_hash, password)


class PlaidItems(db.Model):
    """Data model for plaid_items table.

    Columns include:
    plaid_item_id: auto increment primary key; int
    user_id: user id that the plaid item is associated with; int
    item_id: plaid item id; string
    access_token: token that is associated to user account information
                  for retrieval in plaid; string
    """
    __tablename__ = "plaid_items"
    id = db.Column("plaid_item_id", db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.user_id"))
    item_id = db.Column(db.String, nullable=False)
    access_token = db.Column(db.String, nullable=False)

    # relationships
    accounts = db.relationship("Accounts", backref="plaid_item")


class Accounts(db.Model):
    """Data model for accounts table.

    Columns include:
    account_id: auto increment primary key; int
    user_id: user id that the account is associated with; int
    plaid_id: plaid id that the account is associated with; int
    account_plaid_id: unique id for identification in plaid; string
    account_name: account name; string
    account_type: account type, ex. investment/depository/credit; string
    account_subtype: account subtype, ex. 401k/checking/credit card; string
    """
    __tablename__ = "accounts"
    id = db.Column("account_id", db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.user_id"))
    plaid_id = db.Column(db.Integer,
                         db.ForeignKey("plaid_items.plaid_item_id"))
    account_plaid_id = db.Column(db.String, nullable=False)
    account_name = db.Column(db.String)
    account_type = db.Column(db.String)
    account_subtype = db.Column(db.String)

    # relationships
    transaction = db.relationship("Transaction", backref="account")


class Transaction(db.Model):
    """Data model for transaction table.

    Columns include:
    transaction_id: auto increment primary key; int
    user_id: user id that the transaction is associated with; int
    account_id: account id that the transaction is associated with; int
    trans_amount: transaction amount; decimal(10, 2)
    category_id: category id in plaid; int
    is_preferred_saving: whether the transaction is a preferred saving
                         category; string
    trans_date: date of the transaction; date
    post_date: date when the transaction is posted on user's account; date
    merchant_category: multiple categories possible; string
    merchant_address: merchant address; string
    merchant_city: merchant city; string
    merchant_state: merchant state; string
    merchant_country: merchant country; string
    merchant_postal_code: merchant postal code; string
    merchant_longitude: merchant longitude; string
    merchant_latitude: merchant latitude; string
    """
    __tablename__ = "transaction"
    id = db.Column("transaction_id", db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.user_id"))
    account_id = db.Column(db.Integer,
                           db.ForeignKey("accounts.account_id"))
    trans_amount = db.Column(db.Numeric(10, 2), nullable=False)
    category_id = db.Column(db.Integer)
    is_preferred_saving = db.Column(db.String)
    trans_date = db.Column(db.Date, nullable=False)
    post_date = db.Column(db.Date)
    merchant_category = db.Column(db.String)
    merchant_address = db.Column(db.String)
    merchant_city = db.Column(db.String)
    merchant_state = db.Column(db.String)
    merchant_country = db.Column(db.String)
    merchant_postal_code = db.Column(db.String)
    merchant_longitude = db.Column(db.String)
    merchant_latitude = db.Column(db.String)


class SavingsHistory(db.Model):
    """Data model for savings_history table.

    Columns include:
    savings_id: auto increment primary key; int
    user_id: id of the user that made the saving; int
    savings_amount: savings amount; decimal(10, 2)
    total_savings: total savings the user has made so far; decimal(10, 2)
    predicted_savings: predicted savings the user will make; decimal(10, 2)
    transfer_date: date when the savings are transferred to a
                   savings/investment account; date
    update_date: date when the savings entry is updated in the system; date
    """
    __tablename__ = "savings_history"
    id = db.Column("savings_id", db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.user_id"))
    savings_amount = db.Column(db.Numeric(10, 2), nullable=False)
    total_savings = db.Column(db.Numeric(10, 2), nullable=False)
    predicted_savings = db.Column(db.Numeric(10, 2))
    transfer_date = db.Column(db.Date, nullable=False)
    update_date = db.Column(db.Date, nullable=False)


class Habits(db.Model):
    """Data model for habits table.

    Columns include:
    habits_id: auto increment primary key; int
    user_id: id of the user that made the habit; int
    habit_name: name of the habit user created; string
    habit_category: category of the habit; string
    time_minute: minute of the reminder (0-59); int
    time_hour: hour of the reminder (0-23); int
    time_day_of_week: day of week of the reminder, including 3 values:
                      "weekday", "weekend", "everyday"; string
    """
    __tablename__ = "habits"
    id = db.Column("habits_id", db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.user_id"))
    habit_name = db.Column(db.String, nullable=False)
    habit_category = db.Column(db.String, nullable=False)
    time_minute = db.Column(db.Integer, nullable=False)
    time_hour = db.Column(db.Integer, nullable=False)
    time_day_of_week = db.Column(db.String, nullable=False)


class Coin(db.Model):
    """Data model for coin table.

    Columns include:
    log_id: auto increment primary key; int
    user_id: id of the user that the coin is associated with; int
    coin_amount: number of coins added or subtracted; int
    log_date: date when the coin transaction occurs; date
    description: why the coins are added or subtracted, including 3 values:
                 login, saving, and lottery; string
    """
    __tablename__ = "coin"
    id = db.Column("log_id", db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.user_id"))
    coin_amount = db.Column(db.Integer, nullable=False)
    log_date = db.Column(db.Date, nullable=False)
    description = db.Column(db.String, nullable=False)


class Lottery(db.Model):
    """Data model for lottery table.

    Columns include:
    lottery_id: auto increment primary key; int
    lottery_name: name of the lottery; string
    start_date: date when the lottery starts; datetime
    end_date: date when the lottery ends; datetime
    category: lottery category; string
    cost: number of coins that the lottery costs; int
    winner_user_id: user id of the lottery winner; int
    """
    __tablename__ = "lottery"
    id = db.Column("lottery_id", db.Integer, primary_key=True)
    lottery_name = db.Column(db.String, nullable=False)
    start_date = db.Column(db.DateTime, nullable=False)
    end_date = db.Column(db.DateTime, nullable=False)
    category = db.Column(db.String, nullable=False)
    cost = db.Column(db.Integer, nullable=False)
    winner_user_id = db.Column(db.Integer, default=None)

    # relationships
    lottery_log = db.relationship("UserLotteryLog", backref="lottery")


class UserLotteryLog(db.Model):
    """Data model for user_lottery_log table.

    Columns include:
    lottery_log_id: auto increment primary key; int
    user_id: id of the user; int
    lottery_id: id of the lottery that the user entered; int
    entries: number of entries for the lottery; int
    """
    __tablename__ = "user_lottery_log"
    id = db.Column("lottery_log_id", db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.user_id"))
    lottery_id = db.Column(db.Integer, db.ForeignKey("lottery.lottery_id"))
    entries = db.Column(db.Integer, nullable=False, default=1)


class RegistrationForm(FlaskForm):
    """Class for registration form"""
    first_name = StringField("First Name:",
                             validators=[
                                 DataRequired(message='Input Required')])
    last_name = StringField("Last Name:", validators=[
        DataRequired(message='Input Required')])
    email = StringField("Email Address:", validators=[
        DataRequired(message='Input Required')])
    phone = StringField("Phone Number:", validators=[
        DataRequired(message='Input Required')])
    password = PasswordField("Create a Password:", validators=[
        DataRequired(message='Input Required')])
    submit = SubmitField("Submit")


class LogInForm(FlaskForm):
    """Class for login form"""
    email = StringField("Email:", validators=[DataRequired()])
    password = PasswordField("Password:", validators=[DataRequired()])
    submit = SubmitField("Submit")


class HabitForm(FlaskForm):
    """Class for habit formation form"""
    habit_name = StringField("Habit Name:", validators=[DataRequired()])
    habit_category = SelectField("Habit Category:",
                                 choices=[('Coffee', 'Coffee'),
                                          ('Lunch', 'Lunch'),
                                          ('Transportation',
                                           'Transportation')],
                                 validators=[DataRequired()])
    time_minute = SelectField("Minute:",
                              choices=[(str(i), str(i))
                                       for i in range(60)],
                              validators=[DataRequired()])
    time_hour = SelectField("Hour:", choices=[(str(i), str(i))
                                              for i in range(24)],
                            validators=[DataRequired()])
    time_day_of_week = SelectField("Day Of Week:",
                                   choices=[('weekday', 'Weekday'),
                                            ('weekend', 'Weekend'),
                                            ('everyday', 'Everyday')],
                                   validators=[DataRequired()])
    submit = SubmitField("Submit")


@login_manager.user_loader
def load_user(id):
    """Return a user object from the user id stored in the session"""
    return User.query.get(int(id))


db.create_all()
db.session.commit()
