from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func
from sqlalchemy import text
from sqlalchemy.orm import sessionmaker



app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///michelin_guide.db'
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {'isolation_level': 'SERIALIZABLE'}
app.config['SECRET_KEY'] = 'mmg000817'  # Replace with a real secret key
db = SQLAlchemy(app)
def create_custom_session():
    return sessionmaker(bind=db.engine)()





class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True)
    password_hash = db.Column(db.String(128))

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Restaurant(db.Model):
    website = db.Column(db.String(120), primary_key=True, index=True)
    name = db.Column(db.String(80), nullable=False)
    address = db.Column(db.String(120), nullable=False)
    rate = db.Column(db.Float, nullable=False)
    comment = db.Column(db.String(500))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

def get_restaurant_by_website(website):
    stmt = text("SELECT * FROM restaurant WHERE website = :website")
    result = db.engine.execute(stmt, website=website)
    return result.fetchone()

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/restaurant', methods=['GET', 'POST'])
def restaurant():
    if request.method == 'POST':
        if 'user_id' not in session:
            return redirect(url_for('login'))

        # Create a new session instance
        custom_session = create_custom_session()
        try:
            name = request.form['name']
            address = request.form['address']
            website = request.form['website']
            rate = request.form['rate']
            comment = request.form['comment']
            user_id = session['user_id']

            new_restaurant = Restaurant(name=name, address=address, website=website, rate=rate, comment=comment, user_id=user_id)
            custom_session.add(new_restaurant)
            custom_session.commit()
            return redirect(url_for('restaurant'))  # Redirect as needed
        except Exception as e:
            custom_session.rollback()
            return "Error: " + str(e)
        finally:
            custom_session.close()
    return render_template('restaurant.html')




@app.route('/restaurant_list', methods=['GET', 'POST'])
def restaurant_list():
    if request.method == 'POST':
        custom_session = create_custom_session()
        try:
            website = request.form['website']
            rate = request.form['rate']
            comment = request.form['comment']
            restaurant_to_update = custom_session.query(Restaurant).get(website)
            if restaurant_to_update:
                restaurant_to_update.rate = rate
                restaurant_to_update.comment = comment
            custom_session.commit()
            return redirect(url_for('restaurant_list'))
        except Exception as e:
            custom_session.rollback()
            return "Error: " + str(e)
        finally:
            custom_session.close()

    restaurants = Restaurant.query.all()
    avg_rates = db.session.query(Restaurant.website, func.avg(Restaurant.rate)).group_by(Restaurant.website).all()
    return render_template('restaurant_list.html', restaurants=restaurants, avg_rates=avg_rates)


@app.route('/restaurant/<website>', methods=['GET'])
def restaurant_detail(website):
    restaurant = get_restaurant_by_website(website)
    if restaurant is None:
        return "No restaurant found with this website", 404
    else:
        return render_template('restaurant_detail.html', restaurant=restaurant)





@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        custom_session = create_custom_session()
        try:
            username = request.form['username']
            password = request.form['password']
            existing_user = custom_session.query(User).filter_by(username=username).first()
            if existing_user is None:
                new_user = User(username=username)
                new_user.set_password(password)
                custom_session.add(new_user)
                custom_session.commit()
                return 'User created!'
            else:
                return 'User already exists!'
        except Exception as e:
            custom_session.rollback()
            return "Error: " + str(e)
        finally:
            custom_session.close()
    return render_template('signup.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user is not None and user.check_password(password):
            session['user_id'] = user.id  # Store the user's ID in the session
            return redirect(url_for('restaurant'))
        else:
            return 'Invalid username or password'
    return render_template('login.html')


@app.route('/delete_account', methods=['GET', 'POST'])
def delete_account():
    if request.method == 'POST':
        custom_session = create_custom_session()
        try:
            username = request.form['username']
            password = request.form['password']
            user = custom_session.query(User).filter_by(username=username).first()
            if user is not None and user.check_password(password):
                custom_session.delete(user)
                custom_session.commit()
                return redirect(url_for('home'))
        except Exception as e:
            custom_session.rollback()
            return "Error: " + str(e)
        finally:
            custom_session.close()
    return render_template('delete_account.html')



with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)
