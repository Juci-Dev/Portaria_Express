from  flask import Flask, redirect, url_for
from routes import register_blueprints



app = Flask(__name__)
app.config['SECRET_KEY'] = 'CHAVE_sECRETA'

register_blueprints(app)


@app.route('/')
def home():
    return redirect(url_for('morador.cadastro'))

if __name__ == "__main__":
    app.run(debug=False)
