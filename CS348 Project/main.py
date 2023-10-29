# main.py

from flask import Flask, render_template, request

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/restaurant', methods=['GET', 'POST'])
def restaurant():
    if request.method == 'POST':
        # Here you would handle the form submission and add the restaurant to your database
        pass

    # Render the restaurant page which could include a form to add a new restaurant
    return render_template('restaurant.html')

if __name__ == '__main__':
    app.run(debug=True)
