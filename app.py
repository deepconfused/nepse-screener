import requests
from flask import Flask, render_template

app = Flask(__name__)

API_URL = "https://nepalipaisa.com/api/GetStockLive"

@app.route('/')
def home():
    try:
        response = requests.post(API_URL)
        response.raise_for_status() 

        # This gives us a Python dictionary.
        api_data_dictionary = response.json()
        
        # --- THIS IS THE CRUCIAL DEBUGGING LINE ---
        # It will print the keys of the dictionary to your terminal.
        print(f"DEBUG: The API returned a dictionary with these keys: {api_data_dictionary.keys()}")
        
        # The app will still crash after this, which is OK. We just need the output.
        # We will assume a placeholder key for now.
        stocks_list = [] # Placeholder
        return render_template('index.html', stocks=stocks_list)


    except Exception as e:
        import traceback
        traceback.print_exc()
        return "<h1>An error occurred. Check the terminal for the DEBUG message.</h1>"

if __name__ == '__main__':
    app.run(debug=True)