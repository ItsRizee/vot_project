import os
import base64
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
    # Fetch all journeys from Firestore
    journeys = []
    collection_ref = db.collection('journeys')
    docs = collection_ref.stream()
    for doc in docs:
        journey_data = doc.to_dict()
        journey_data['id'] = doc.id

        # Fetch images from Cloud Storage
        bucket = storage_client.bucket(doc.id.lower())
        blobs = list(bucket.list_blobs())
        if blobs:
            image_blob = blobs[0]
            image_content = image_blob.download_as_bytes()
            image_base64 = base64.b64encode(image_content).decode('utf-8')
            journey_data['image_base64'] = image_base64
        else:
            journey_data['image_base64'] = None

        journeys.append(journey_data)

    return render_template('home.html', journeys=journeys)


@app.route('/journey/<journey_id>')
def journey_details(journey_id):
    # Retrieve journey details from Firestore
    journey_ref = db.collection('journeys').document(journey_id)
    journey_data = journey_ref.get().to_dict()

    # Fetch images from Cloud Storage
    bucket = storage_client.bucket(journey_id.lower())
    blobs = list(bucket.list_blobs())
    images = []
    if blobs:
        for blob in blobs:
            image_base64 = base64.b64encode(blob.download_as_bytes()).decode('utf-8')
            images.append(image_base64)

    return render_template('more_info.html', journey=journey_data, images=images)


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
        document = db.collection('journeys').document()
        document.set({
            'title': title,
            'country': country,
            'description': description
        })

        bucket = storage_client.bucket(document.id.lower())

        # Create the bucket if it doesn't exist
        if not bucket.exists():
            bucket.create()

        # Upload images to the bucket
        for image in images:
            blob = bucket.blob(image.filename)
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
