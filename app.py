import logging
import re

from dotenv import load_dotenv
from flask import Flask, abort, render_template, request
from flask_caching import Cache
from markupsafe import escape

from main import AddressDetails, get_gmaps_client

load_dotenv()

config = {
    "CACHE_TYPE": "SimpleCache",  # Flask-Caching related configs
    "CACHE_DEFAULT_TIMEOUT": 600
}

app = Flask(__name__)
app.config.from_mapping(config)

cache = Cache(app)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# cache test
logger.info("setting gmaps client in cache...")
cache.set("gmaps", get_gmaps_client())

logger.info("loading gmaps client...")
with app.app_context():
    gmaps = cache.get("gmaps")

@app.before_request
def limit_payload():
    if request.content_length and request.content_length > 1024 * 10:  # 10 KB
        abort(413, "Request too large")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/lookup', methods=['POST'])
def lookup_address():
    try:
        # Get form data
        street = request.form.get('streetAddress', '').strip()
        street_safe = escape(street)
        if len(street_safe) > 200:
            abort(400, "Street address is too long")

        zip = request.form.get('ZIPCode', '').strip()
        zip_safe = escape(zip)
        if not re.match(r"^\d{5}(-\d{4})?$", zip_safe):
            abort(400, "Invalid ZIP code")

        logger.info("Loading gmaps...")
        with app.app_context():
            gmaps = cache.get("gmaps")
            if gmaps == None:
                logger.info("gmaps not found in cache. Storing in cache.")
                cache.set("gmaps", get_gmaps_client())
                logger.info("Loading gmaps...")
                gmaps = cache.get("gmaps")
                
        # Call the main function
        result = AddressDetails().address_lookup(gmaps, street_safe, zip_safe)

        # fix params = params
        return render_template('result.html', params=[street_safe, zip_safe], result=result)
    
    except Exception:
        logger.exception("An error occurred.")
        return render_template('error.html', error="Address not found."), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
