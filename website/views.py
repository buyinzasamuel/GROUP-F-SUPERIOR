from flask import Blueprint, render_template, session, redirect, url_for

views = Blueprint('views', __name__)

@views.route('/')
def home():
    if 'email' in session:
        return render_template('home.html', username=session['email'])
    return redirect(url_for('auth.login'))