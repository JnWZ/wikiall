# app/routes.py
from flask import render_template
from app import app

# Définition des routes

@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')

# Vous pouvez ajouter d'autres routes ici en fonction de vos besoins
