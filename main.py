from flask import Flask, render_template, request

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/new_journey', methods=['POST', 'GET'])
def new_journey():
    if request.method == 'POST':
        # Process the form data
        title = request.form['title']
        country = request.form['country']
        description = request.form['description']
        images = request.files.getlist('image')


    return render_template('new_journey.html')

@app.route('/contact', methods=['POST', 'GET'])
def contact():
    if request.method == 'POST':
        # Process the form data
        name = request.form['name']
        email = request.form['email']
        message = request.form['message']


    return render_template('contact.html')

@app.route('/about')
def about():
    return render_template('about.html')

if __name__ == '__main__':
    app.run()
