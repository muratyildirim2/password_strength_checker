# app.py
from flask import Flask, render_template, request
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
import joblib
from tokenizer import word

def validate_password(password, strength):
    validation_errors = []
    faults = 0
    if len(password) < 8:
        validation_errors.append("Şifre en az 8 karakter içermelidir.")
        faults+=1
    if not any(c.isupper() for c in password):
        validation_errors.append("Şifre en az bir büyük harf içermelidir.")
        faults+=1
    if not any(c.islower() for c in password):
        validation_errors.append("Şifre en az bir küçük harf içermelidir.")
        faults+=1
    if not any(c.isdigit() for c in password):
        validation_errors.append("Şifre en az bir sayı içermelidir.")
        faults+=1
    if not any(c in "!@#$%^&*()-_=+[]{}|;:'\",.<>?/" for c in password):
        validation_errors.append("Şifre en az bir özel karakter içermelidir.")
        faults+=1

        if faults==4 :
            strength-=1
            strength = max(strength,0)


    # Hataları newline ile birleştirerek döndür
    return "<br>".join(validation_errors), strength


app = Flask(__name__)

model = joblib.load("password_strength_model.pkl")
tdif = joblib.load("password_tfidf.pkl")

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/predict_strength', methods=['POST'])
def predict_strength():
    user_password = request.form['password']

    user_data = tdif.transform([user_password]).toarray()

    predicted_strength = model.predict(user_data)[0]

    validation_errors, predicted_strength = validate_password(user_password, predicted_strength)

    strength_mapping = {0: 'Weak', 1: 'Medium', 2: 'Strong'}
    
    predicted_label = strength_mapping.get(predicted_strength, 'Unknown')
    if validation_errors:
        feedback = "".join(validation_errors)
        return render_template('index.html', password=user_password,prediction=predicted_label, feedback=feedback)

    return render_template('index.html', prediction=predicted_label, password=user_password)

if __name__ == '__main__':
    app.run(debug=True, port=8000)
