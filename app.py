
from flask import Flask, render_template, request, jsonify
from main import address_lookup

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/lookup', methods=['POST'])
def lookup_address():
    try:
        # Get form data
        street = request.form.get('streetAddress')
        zip = request.form.get('ZIPCode')
        
        # Call the main function
        result = address_lookup(street, zip)

        # fix params = params
        return render_template('result.html', params=[street, zip], result=result)
    except Exception as e:
        return render_template('error.html', error=str(e))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
