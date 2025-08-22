
from flask import Flask, render_template, request, jsonify
from main import address_and_county

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/lookup', methods=['POST'])
def lookup_address():
    try:
        # Get form data
        params = {
            "streetAddress": request.form.get('streetAddress', ''),
            "secondaryAddress": request.form.get('secondaryAddress', ''),
            "city": request.form.get('city', ''),
            "state": request.form.get('state', ''),
            "ZIPCode": request.form.get('ZIPCode', '')
        }
        
        # Call the main function
        result = address_and_county(params)
        
        return render_template('result.html', params=params, result=result)
    except Exception as e:
        return render_template('error.html', error=str(e))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
