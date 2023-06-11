import os

from flask import Flask, render_template, request
from firebase_admin import credentials, initialize_app, firestore
from google.cloud import storage

cred = credentials.Certificate("api/key.json")
default_app = initialize_app(cred)

# Initialize Flask app
app = Flask(__name__)

# Initialize Firestore DB
db = firestore.client(app=default_app)

# Initialize Cloud Storage client
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'api/storage_key.json'
storage_client = storage.Client()


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
        images = request.files.getlist('images')
        print(images)

        # Add contact data to database
        contact_reference = db.collection('journeys').document()
        contact_reference.set({
            'title': title,
            'country': country,
            'description': description
        })

        bucket = storage_client.get_bucket('journeys-storage-2023')

        # Upload images to the bucket
        for image in images:
            image_extension = os.path.splitext(image.filename)[1]
            image_filename = f"{contact_reference.id}{image_extension}"
            blob = bucket.blob(image_filename)
            print(type(image))
            blob.upload_from_file(image.stream)

    return render_template('new_journey.html')


@app.route('/contact', methods=['POST', 'GET'])
def contact():
    if request.method == 'POST':
        # Process the form data
        name = request.form['name']
        email = request.form['email']
        message = request.form['message']

        # Add contact data to database
        contact_reference = db.collection('contacts').document()
        contact_reference.set({
            'name': name,
            'email': email,
            'message': message
        })

    return render_template('contact.html')


@app.route('/about')
def about():
    return render_template('about.html')


if __name__ == '__main__':
    app.run()
