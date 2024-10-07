import json  # Add this import at the top
from flask import Flask, render_template, request, redirect, url_for, flash
from analysis import analyze_word, create_pie_chart  # Import the function

app = Flask(__name__)
app.secret_key = "supersecretkey"  # Needed for handling sessions securely

# Route for the homepage
@app.route('/')
def index():
    return render_template('index.html')

# Route for handling form submissions (calculator logic here)
@app.route('/calculate', methods=['POST'])
def calculate():
    if request.method == 'POST':
        try:
            # Get inputs from the form (simple calculator example)
            number1 = float(request.form['number1'])
            number2 = float(request.form['number2'])
            operation = request.form['operation']
            
            # Perform calculation based on the selected operation
            if operation == 'add':
                result = number1 + number2
            elif operation == 'subtract':
                result = number1 - number2
            elif operation == 'multiply':
                result = number1 * number2
            elif operation == 'divide':
                if number2 != 0:
                    result = number1 / number2
                else:
                    flash("Cannot divide by zero", 'error')
                    return redirect(url_for('index'))

            return render_template('index.html', result=result)
        except ValueError:
            flash("Invalid input. Please enter valid numbers.", 'error')
            return redirect(url_for('index'))

# Route for handling word analysis
@app.route('/word_analysis', methods=['POST'])
def word_analysis():
    if request.method == 'POST':
        word = request.form['word']
        keep_case = request.form.get('keep_case') == 'true'  # Get the checkbox value
        try:
            # Call the analyze_word function with keep_case
            df = analyze_word(word, keep_case)
            print(df)  # Debugging line to check data

            if not df.empty:
                fig_html = create_pie_chart(df)
            else:
                fig_html = "<p>No data available for the entered word.</p>"

            # Convert the grouped data to a list of dicts
            results = df.to_dict(orient='records')

            return render_template('index.html', word=word, results=results, fig_html=fig_html)
        except Exception as e:
            flash("Error processing the word analysis.", 'error')
            return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
