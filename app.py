from flask import Flask, render_template, request, redirect, url_for
import MySQLdb
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_wtf import Form
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Length
import mistune
from flask import request, jsonify
app = Flask(__name__, template_folder='app\\templates')
app.config['SECRET_KEY'] = 'your-secret-key' # add a secret key for session handling


# Configuration de la base de données
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'wzwiki2024'
app.config['MYSQL_DB'] = 'wikibase'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

mysql = MySQLdb.connect(host=app.config['MYSQL_HOST'], user=app.config['MYSQL_USER'],
                        password=app.config['MYSQL_PASSWORD'], db=app.config['MYSQL_DB'])

def req(prompt, params=None):
    cursor = mysql.cursor()
    if params:
        cursor.execute(prompt, params)
    else:
        cursor.execute(prompt)
    data = cursor.fetchall()
    cursor.close()
    return data


class SearchForm(Form):
    title = StringField('Search', validators=[DataRequired(), Length(min=3, max=50)])
    submit = SubmitField('Search')

# Home page
@app.route('/')
def index():
    form = SearchForm()
    articles = req("SELECT * FROM articles")
    return render_template('index.html', articles=articles, form=form)

@app.route('/identifiant', methods=['GET','POST'])
def identifiant():
    return render_template('identifiant.html')

@app.route('/verifier_identifiant', methods=['POST'])
def verifier_identifiant():
    identifiant = request.form.get('identifiant')

    if identifiant:
        id = req("SELECT COUNT(*) FROM utilisateurs WHERE identifiant = %s;", (identifiant,))
        print(id)
        yes = id[0][0]
        if yes == 1 :
            return redirect(url_for('mot_de_passe', identifiant=identifiant))
        else : 
            flash('Utilisateur inconnu.')
            return redirect(url_for('identifiant'))
    else:
        flash('Veuillez entrer un identifiant valide.')
        return redirect(url_for('identifiant'))

@app.route('/mot_de_passe/<identifiant>', methods=['GET', 'POST'])
def mot_de_passe(identifiant):
    return render_template('mot_de_passe.html', identifiant=identifiant)

@app.route('/verifier_mot_de_passe', methods=['POST'])
def verifier_mot_de_passe():
    identifiant = request.form.get('identifiant')
    mot_de_passe = request.form.get('mot_de_passe')

    if identifiant and mot_de_passe:
        password = req("select mot_de_passe from utilisateurs where identifiant = %s", (identifiant,))
        print(password)
        pswd = password[0][0]
        if pswd == mot_de_passe:
            return redirect(url_for('index'))
        else :
            flash("Mot de passe incorrect. Veuillez réessayer.")
            return redirect(url_for('mot_de_passe', identifiant=identifiant))
    else:
        flash('Identifiant ou mot de passe incorrerrrrrrrrrrrrrrrrct.')
        return redirect(url_for('identifiant'))


@app.route('/new_user')
def new_user():
    return render_template('new_user.html')


@app.route('/article/<int:article_id>', methods=['GET', 'POST'])
def article(article_id):
        # Récupérer les informations de l'article à partir de la base de données
    article = req("SELECT * FROM articles WHERE article_id = %s" % article_id)
    if article:
        # Récupérer les sections associées à l'article
        sections = req("SELECT * FROM sections WHERE article_id = %s ORDER BY ordre ASC" % article_id)

        if request.method == 'POST':
            # Mettre à jour le titre de l'article
            title = request.form['title-input']
            req("UPDATE articles SET titre = %s WHERE article_id = %s", (title, article_id))

            # Mettre à jour les sections de l'article
            for section in sections:
                input_id = f'section-{section[0]}-input'
                if section[3] == 'titre':
                    content = request.form[input_id]
                elif section[3] == 'texte':
                    content = request.form[input_id]
                elif section[3] == 'tableau':
                    content = request.form[input_id]
                    # Convertir le contenu du tableau en chaîne de caractères
                    content = content.replace('<table>', '').replace('</table>', '').replace('<tr>', '|').replace('</tr>', '|\n').replace('<td>', '|').replace('</td>', '|')
                req("UPDATE sections SET contenu = %s WHERE section_id = %s", (content, section[0]))

            # Rediriger vers la page de l'article
            return render_template('article.html', article_id=article_id)

        # Afficher la page de l'article avec le formulaire d'édition
        return render_template('article.html', article=article[0], **{'sections' : sections})
    else:
        return "Article non trouvé."

@app.route('/article/<int:article_id>/save', methods=['POST'])
def save(article_id):
    article_data = req("SELECT * FROM articles WHERE article_id = %s" % article_id)

    if article_data:

        # Récupérer les sections associées à l'article
        sections = req("SELECT * FROM sections WHERE article_id = %s ORDER BY ordre ASC" % article_id)

        if request.method == 'POST':
            data = request.get_json()  # Récupérer les données JSON envoyées par la requête AJAX

            # Mettre à jour le titre de l'article
            title = data['title']
            req("UPDATE articles SET titre = %s WHERE article_id = %s", (title, article_id))
            print(data)
            # Mettre à jour les sections de l'article
            for i, section in enumerate(sections):
                content = data['sections'][i]
                if section[3] == 'tableau' and section[4]!= None and section[4]!='None':
                    # Convertir le contenu du tableau en chaîne de caractères
                    content = '\n'.join(['|'.join(row) for row in content])
                req("UPDATE sections SET contenu = %s WHERE section_id = %s", (content, section[0]))

    return render_template('article.html', article=article_id)


@app.route('/new_wiki', methods=['POST'])
def new_wiki():
    
    new_id = req("""insert into articles (titre, contenu) values ("Nouvel article", "Commencez à écrire...");""")
    new_id = req("select last_insert_id() from articles")
    print(new_id)
    article_id = new_id[0][0]
    return redirect(url_for('article', article_id = article_id))



@app.route('/add_section', methods=['POST'])
def add_section():
    article_id = request.form['article_id']
    section_type = request.form['section_type']

    add_new_section_to_article(article_id, section_type)

    # Redirigez l'utilisateur vers la page de l'article
    return redirect(url_for('article', article_id=article_id))




def add_new_section_to_article(article_id, section_type):
    # Connectez-vous à la base de données
    conn = mysql
    cursor = conn.cursor()

    # Récupérez le dernier ordre de section pour l'article
    cursor.execute("SELECT MAX(ordre) AS last_order FROM sections WHERE article_id = %s", (article_id,))
    last_order = cursor.fetchone()['last_order'] or 0

    # Ajoutez une nouvelle section à l'article dans la base de données
    if section_type == 'title':
        content = 'Titre par défaut'
    elif section_type == 'text':
        content = 'Texte par défaut'
    elif section_type == 'table':
        content = '| Colonne 1 | Colonne 2 |\n| Cellule 1 | Cellule 2 |'
    cursor.execute("INSERT INTO sections (article_id, type, contenu, ordre) VALUES (%s, %s, %s, %s)", (article_id, section_type, content, last_order + 1))

    # Commettez la transaction
    conn.commit()

    # Fermez la connexion à la base de données
    cursor.close()
    conn.close()



#search page
@app.route('/search',methods=['POST'])
def search():
    query = request.form['query']
    # échapper les caractères spéciaux dans la chaîne de requête
    query = query.replace('%', '\\%').replace('_', '\\_')

    sql = "SELECT * FROM articles WHERE titre LIKE %s"
    val = ("%%%s%%" % query,)  # les pourcentages doivent être doublés pour être échappés
    result = req(sql, val)

    return render_template('search.html', query=query, results=result)








if __name__ == '__main__':
    app.run(debug=True)

