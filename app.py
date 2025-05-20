from flask import Flask, render_template,request

app=Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')


@app.route('/result', methods=['POST'])
def result():
    num1 = float(request.form['num1'])
    num2 = float(request.form['num2'])
    result = num1 + num2
    
    return render_template('result.html', result=result, number1=num1, number2=num2)




if __name__=="__main__":
    app.run(debug=True)