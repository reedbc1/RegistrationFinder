
from flask import Flask, render_template, request, jsonify, abort
from geocoder2 import AddressDetails
import re
from markupsafe import escape
import logging
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

@app.before_request
def limit_payload():
    if request.content_length and request.content_length > 1024 * 10:  # 10 KB
        abort(413, "Request too large")

@app.route('/')
def index():
    return render_template('index.html')

limiter = Limiter(get_remote_address, app=app)

@app.route('/lookup', methods=['POST'])
@limiter.limit("10 per minute")
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

        # Call the main function
        result = AddressDetails().address_lookup(street_safe, zip_safe)

        # fix params = params
        return render_template('result.html', params=[street_safe, zip_safe], result=result)
    
    except Exception as e:
        logging.exception(str(e))
        return render_template('error.html', error="Address not found."), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
