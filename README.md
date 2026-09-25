# Campus Request

Campus Request est une application web développée avec **Flask** et **PostgreSQL** permettant aux élèves du campus skolae d'aix en provence d'avoir un point d'entrée unique pour SIGNALER / DEMANDER / PROPOSER toute choses aux différents services administratifs et associatif du campus. C'est un site qui sera modéré par une association étudiante afin de facilité le relais avec les différents corps administratifs du campus. Le but de Campus Request est de pré-mâcher le travail de modération des demandes et signalements des élèves, ainsi que de facilité l'accès aux services et informations du campus a ces derniers. A terme le site permettra aussi d'encourager les projets et participations à la vie étudiante.

Le projet comprend actuellement :

- inscription et authentification étudiant ;
- confirmation du compte étudiant et administrateur par email ;
- création et historique des tickets ;
- classification par nature et sujets/tags ;
- routage vers les services administratifs ;
- interface administrateur ;
- changement de statut des tickets ;
- réorientation vers un service ;
- envoi d'emails avec Brevo ;
- moteur de modération en cours de développement.

Evolutions envisagées : 
- création d'un fil d'actualité de la vie du campus, relié avec les instagram du BDE et de Skolae ;
- option de dépôt d'annonce pour des appel à projets pour mettre en contact les étudiants entre eux
  
---

# 1. Stack technique

Le projet utilise principalement :

- Python 3.13
- Flask
- Flask-SQLAlchemy
- Flask-Migrate
- SQLAlchemy
- Alembic
- PostgreSQL
- Brevo pour les emails
- HTML / CSS / JavaScript
- Git / GitHub

---

# 2. Version de Python

## IMPORTANT

La version de référence pour Campus Request est :

```text
Python 3.13
```
notamment utilisé avec :
```text
Python 3.13.15
```
Évitez de créer l'environnement avec Python 3.14 sans avoir vérifié la compatibilité de toutes les dépendances.
Nous avons notamment rencontré des problèmes d'installation de dépendances avec Python 3.14.

Vérifiez :

```bash
python3.13 --version
```
Exemple attendu :
```text
Python 3.13.15
```

---

# 3. Prérequis

Avant de commencer, veuillez installer :

- Git
- Python 3.13
- module Python `venv`
- PostgreSQL
- pip
- un éditeur de code, par exemple VS Code

Vérifications :

```bash
git --version
python3.13 --version
psql --version
```

---

# 4. Installation de Python 3.13 sur Ubuntu 24.04

Cette section est utile si `python3.13` n'existe pas.

Vérifier d'abord :

```bash
python3.13 --version
```

Si Python 3.13 n'est pas disponible, sur Ubuntu 24.04 :

```bash
sudo apt update
sudo apt install software-properties-common
```

Ajouter le dépôt permettant d'installer Python 3.13 :

```bash
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt update
```

Puis :

```bash
sudo apt install python3.13 python3.13-venv
```

Vérifier :

```bash
command -v python3.13
python3.13 --version
```

Exemple :

```text
/usr/bin/python3.13
Python 3.13.15
```

## Ne pas créer d'alias Python

Ne pas faire :

```bash
alias python='/usr/bin/python3.13.15'
```

L'exécutable est généralement :

```text
/usr/bin/python3.13
```

et non :

```text
/usr/bin/python3.13.15
```

Il n'est de toute façon pas nécessaire de créer un alias : l'environnement virtuel fournit automatiquement la bonne commande `python`.

---

# 5. Cloner Campus Request

Ne pas utiliser `git init` pour récupérer le projet.

Cloner le dépôt :

```bash
git clone <URL_DU_REPOSITORY>
```

Puis :

```bash
cd campus-request-skolae
```

Vérifier que l'on est au bon endroit :

```bash
pwd
ls
```

Le projet doit notamment contenir :

```text
app.py
config.py
extensions.py
requirements.txt
migrations/
models/
routes/
services/
static/
templates/
```

Vérifier Git :

```bash
git status
git branch --show-current
git remote -v
```

---

# 6. Créer une branche personnelle

Ne pas développer directement sur `main`.

Commencer par mettre `main` à jour :

```bash
git switch main
git pull origin main
```

Puis créer une branche :

```bash
git switch -c prenom
```

Exemple :

```bash
git switch -c tristan
```

La publier :

```bash
git push -u origin tristan
```

---

# 7. Créer l'environnement virtuel

À la racine de Campus Request :

```bash
/usr/bin/python3.13 -m venv .venv
```

ou :

```bash
python3.13 -m venv .venv
```

Activer l'environnement :

```bash
source .venv/bin/activate
```

Le terminal doit maintenant commencer par :

```text
(.venv)
```

## Vérification indispensable

```bash
python --version
which python
```

Résultat attendu :

```text
Python 3.13.x
/home/<utilisateur>/.../campus-request-skolae/.venv/bin/python
```

Par exemple :

```text
Python 3.13.15
/home/triss/dev/campus-request-skolae/.venv/bin/python
```

Si `python --version` affiche Python 3.14, le `.venv` a été créé avec le mauvais interpréteur.

Dans ce cas :

```bash
deactivate
rm -rf .venv

/usr/bin/python3.13 -m venv .venv
source .venv/bin/activate

python --version
which python
```

---

# 8. Attention : `.venv` doit être un dossier

Vérifier :

```bash
ls -ld .venv
```

Le résultat doit commencer par :

```text
d
```

par exemple :

```text
drwxr-xr-x ... .venv
```

Le contenu doit ressembler à :

```bash
ls .venv
```

```text
bin
include
lib
pyvenv.cfg
```

Si `.venv` apparaît comme un simple fichier :

```text
-rw-r--r-- ... .venv
```

il faut le supprimer :

```bash
rm .venv
```

puis recréer correctement l'environnement.

---

# 9. Installer les dépendances Python

Avec `(.venv)` actif :

```bash
python -m pip install --upgrade pip
```

Puis :

```bash
python -m pip install -r requirements.txt
```

Vérifier l'intégrité des dépendances :

```bash
python -m pip check
```

Résultat attendu :

```text
No broken requirements found.
```

---

# 10. Vérifier Flask et SQLAlchemy

Tester les imports :

```bash
python -c "import flask; print('Flask OK')"
python -c "import sqlalchemy; print('SQLAlchemy OK', sqlalchemy.__version__)"
python -c "import flask_sqlalchemy; print('Flask-SQLAlchemy OK')"
python -c "import flask_migrate; print('Flask-Migrate OK')"
```

Résultat attendu :

```text
Flask OK
SQLAlchemy OK ...
Flask-SQLAlchemy OK
Flask-Migrate OK
```

Attention : pour afficher la version SQLAlchemy, la syntaxe correcte est :

```python
sqlalchemy.__version__
```

et non :

```python
sqlalchemy.version
```

---

# 11. Vérifier Flask

```bash
which flask
```

Le résultat doit pointer vers le `.venv` :

```text
/home/<utilisateur>/.../campus-request-skolae/.venv/bin/flask
```

Il ne doit pas pointer vers :

```text
/usr/bin/flask
```

ou vers les packages Python système.

---

# 12. Configuration de l'application

Campus Request charge sa configuration depuis :

```text
config.py
```

La configuration actuelle attend notamment :

```python
SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL")
SECRET_KEY = os.getenv("SECRET_KEY")

BREVO_API_KEY = os.getenv("BREVO_API_KEY")
SMTP_SENDER = os.getenv("SMTP_SENDER")

BASE_URL = os.getenv(
    "BASE_URL",
    "http://localhost:5000"
)

SOCKS_PROXY = os.getenv("SOCKS_PROXY")
```

Ces valeurs sont chargées depuis un fichier local :

```text
.env
```

---

# 13. Créer `.env`

Le repository contient :

```text
.env.example
```

Créer sa configuration locale :

```bash
cp .env.example .env
```

Puis :

```bash
nano .env
```

Structure :

```env
DATABASE_URL=postgresql://UTILISATEUR:MOT_DE_PASSE@localhost:5432/campus_request

SECRET_KEY=

BREVO_API_KEY=
SMTP_SENDER=

BASE_URL=http://localhost:5000/

SOCKS_PROXY=
```

## IMPORTANT

`.env` contient des secrets.

Il ne doit JAMAIS être envoyé sur GitHub.

Vérifier :

```bash
git status
```

`.env` ne doit pas apparaître comme fichier à commit.

---

# 14. Générer une SECRET_KEY

Campus Request utilise `SECRET_KEY` pour sécuriser les sessions Flask.

Générer une clé locale :

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

Copier le résultat dans :

```env
SECRET_KEY=<CLE_GENEREE>
```

Ne jamais partager cette clé publiquement.

---

# 15. Installer PostgreSQL

Vérifier :

```bash
psql --version
```

Exemple :

```text
psql (PostgreSQL) 18.x
```

Vérifier le service :

```bash
sudo systemctl status postgresql
```

Il doit être actif.

Si nécessaire :

```bash
sudo systemctl start postgresql
```

---

# 16. Créer un utilisateur PostgreSQL local

Chaque développeur peut avoir son propre utilisateur PostgreSQL.

Ouvrir PostgreSQL en administrateur :

```bash
sudo -u postgres psql
```

Le terminal doit afficher :

```text
postgres=#
```

Créer un utilisateur.

Exemple :

```sql
CREATE USER campus_tristan WITH PASSWORD 'MOT_DE_PASSE_LOCAL';
```

Il est recommandé d'utiliser un nom correspondant au développeur :

```text
campus_sarah
campus_rayan
campus_tristan
...
```

---

# 17. Créer la base Campus Request

Toujours dans PostgreSQL :

```sql
CREATE DATABASE campus_request OWNER campus_tristan;
```

Adapter le propriétaire au compte créé précédemment.

Vérifier :

```sql
\l
```

La base doit apparaître :

```text
campus_request
```

Quitter :

```sql
\q
```

---

# 18. Tester PostgreSQL indépendamment de Flask

Avant de lancer l'application :

```bash
psql -h localhost -U campus_tristan -d campus_request
```

PostgreSQL demande le mot de passe.

Une fois connecté :

```sql
SELECT current_database(), current_user;
```

Résultat attendu :

```text
current_database | current_user
-----------------+----------------
campus_request   | campus_tristan
```

Puis :

```sql
\q
```

Si cette étape ne fonctionne pas, inutile de lancer Flask : il faut d'abord résoudre le problème PostgreSQL.

---

# 19. Configurer DATABASE_URL

Le `.env` doit correspondre exactement au compte PostgreSQL créé.

Exemple :

```env
DATABASE_URL=postgresql://campus_tristan:MOT_DE_PASSE@localhost:5432/campus_request
```

Format général :

```text
postgresql://USER:PASSWORD@HOST:PORT/DATABASE
```

Donc :

```text
USER     = campus_tristan
PASSWORD = mot de passe PostgreSQL
HOST     = localhost
PORT     = 5432
DATABASE = campus_request
```

Attention : certains caractères spéciaux dans un mot de passe peuvent nécessiter un encodage lorsqu'ils sont utilisés dans une URL.

---

# 20. Vérifier que `.env` est chargé

Sans afficher les secrets :

```bash
python -c "from config import Config; print('DATABASE_URL:', bool(Config.SQLALCHEMY_DATABASE_URI)); print('SECRET_KEY:', bool(Config.SECRET_KEY))"
```

Résultat attendu :

```text
DATABASE_URL: True
SECRET_KEY: True
```

---

# 21. Vérifier que Flask peut charger Campus Request

Avant les migrations :

```bash
flask --app app routes
```

Si tout fonctionne, Flask affiche les routes de l'application.

Exemple :

```text
Endpoint              Methods    Rule
--------------------  ---------  -----------------------------------------
account               GET, POST  /account
admin_dashboard       GET        /admin/dashboard
admin_login           GET, POST  /admin/login
admin_register        GET, POST  /admin/register
admin_ticket_detail   GET        /admin/tickets/<string:public_id>
admin_ticket_service  POST       /admin/tickets/<string:public_id>/service
admin_ticket_status   POST       /admin/tickets/<string:public_id>/status
auth_home             GET        /auth
choix_auth            GET        /choix-auth
choix_register        GET        /choix-register
confirm               GET, POST  /confirm
dashboard             GET, POST  /dashboard
history               GET        /history
home                  GET        /
login                 GET, POST  /login
logout                GET        /logout
register              GET, POST  /register
...
```

Si l'erreur suivante apparaît :

```text
RuntimeError:
Either 'SQLALCHEMY_DATABASE_URI'
or 'SQLALCHEMY_BINDS' must be set.
```

cela signifie généralement que :

```env
DATABASE_URL=
```

est absent ou vide dans `.env`.

---

# 22. Initialiser la base avec Alembic

Le projet possède déjà ses migrations.

NE PAS faire :

```bash
flask db init
```

Le dossier :

```text
migrations/
```

est déjà versionné.

Sur une base locale neuve :

```bash
flask db current
```

Il est normal que cette commande n'affiche aucune révision la première fois.

Vérifier la révision cible :

```bash
flask db heads
```

Puis appliquer les migrations :

```bash
flask db upgrade
```

Enfin :

```bash
flask db current
```

La révision affichée doit correspondre au `head`.

---

# 23. Ne pas utiliser `/create-tables` pour initialiser son environnement

L'application peut contenir une route historique :

```text
/create-tables
```

Pour un environnement de développement correctement versionné, utiliser les migrations Alembic :

```bash
flask db upgrade
```

Cela permet de conserver un schéma cohérent entre les développeurs.

---

# 24. Configuration Brevo

Campus Request utilise Brevo pour envoyer notamment les emails de confirmation.

Les variables concernées sont :

```env
BREVO_API_KEY=
SMTP_SENDER=
BASE_URL=http://localhost:5000/
```

## Créer / utiliser un compte Brevo

Utiliser un compte Brevo autorisé pour le projet.

La clé API doit être récupérée depuis l'espace Brevo prévu à cet effet.

Ne jamais :

- écrire la clé dans `app.py` ;
- écrire la clé dans `config.py` ;
- envoyer la clé sur Discord/Teams/Trello ;
- commit la clé sur GitHub.

La clé doit uniquement être placée dans :

```text
.env
```

Exemple :

```env
BREVO_API_KEY=<CLE_API_BREVO>
```

---

# 25. Configurer l'expéditeur Brevo

`SMTP_SENDER` correspond à l'adresse utilisée comme expéditeur par Campus Request.

Exemple :

```env
SMTP_SENDER=adresse-validee@example.com
```

Cette adresse doit être autorisée/validée côté Brevo selon la configuration du compte.

Le fichier `.env` local ressemble alors à :

```env
DATABASE_URL=postgresql://campus_tristan:MOT_DE_PASSE@localhost:5432/campus_request

SECRET_KEY=<CLE_FLASK>

BREVO_API_KEY=<CLE_API_BREVO>
SMTP_SENDER=<EXPEDITEUR_BREVO>

BASE_URL=http://localhost:5000/

SOCKS_PROXY=
```

---

# 26. BASE_URL et emails

En développement local :

```env
BASE_URL=http://localhost:5000/
```

Cette URL est utilisée pour générer les liens présents dans les emails.

En production, elle devra être remplacée par l'URL publique réelle.

Exemple conceptuel :

```env
BASE_URL=https://campus-request.example.com/
```

Ne pas utiliser l'URL de production dans le `.env` local sans raison.

---

# 27. SOCKS_PROXY

Campus Request prévoit également :

```env
SOCKS_PROXY=
```

Cette variable est optionnelle.

En développement local classique, laisser :

```env
SOCKS_PROXY=
```

Ne renseigner un proxy que si l'environnement réseau utilisé pour Brevo le nécessite réellement.

---

# 28. Tester Brevo

Une fois :

```env
BREVO_API_KEY
SMTP_SENDER
BASE_URL
```

correctement configurés, lancer Campus Request puis tester le parcours d'inscription.

Le test attendu est :

```text
Inscription étudiant
        ↓
Campus Request crée la demande de confirmation
        ↓
Brevo envoie l'email
        ↓
L'étudiant reçoit le message
        ↓
Lien / code de confirmation
        ↓
Compte confirmé
```

Ne pas considérer Brevo comme configuré uniquement parce que Flask démarre.

Il faut vérifier qu'un véritable email arrive sur une adresse de test.

---

# 29. Lancer Campus Request

Une fois :

- Python configuré ;
- `.venv` actif ;
- dépendances installées ;
- `.env` configuré ;
- PostgreSQL accessible ;
- migrations appliquées ;

lancer :

```bash
flask run
```

L'application doit être disponible sur :

```text
http://127.0.0.1:5000
```

ou :

```text
http://localhost:5000
```

---

# 30. Test fonctionnel après installation

Avant de développer, vérifier :

- [ ] page d'accueil accessible ;
- [ ] inscription étudiant accessible ;
- [ ] connexion étudiant accessible ;
- [ ] interface admin accessible ;
- [ ] aucune erreur HTTP 500 ;
- [ ] PostgreSQL reçoit correctement les données ;
- [ ] inscription possible ;
- [ ] email de confirmation reçu si Brevo est configuré ;
- [ ] confirmation possible ;
- [ ] connexion possible ;
- [ ] dashboard étudiant accessible ;
- [ ] création d'un ticket possible ;
- [ ] ticket enregistré en BDD ;
- [ ] ticket visible côté admin ;
- [ ] changement de statut possible ;
- [ ] réorientation vers un service possible ;
- [ ] évolution visible dans l'historique étudiant.

---

# 31. Tests du projet

Avant de commencer à modifier le projet, lancer les tests présents sur la branche.

Le repository contient notamment des tests concernant :

- validation des tickets ;
- routage des tickets ;
- statuts administrateur ;
- services administratifs ;
- confirmation email.

Selon la branche utilisée, d'autres tests peuvent être présents.

Exécuter les tests concernés avant et après une modification.

---

# 32. Workflow Git

Chaque développeur travaille sur sa branche.

Avant de commencer :

```bash
git status
git branch --show-current
git fetch origin
```

Avant un commit :

```bash
git status
git diff
git diff --check
```

Puis :

```bash
git add <fichiers>
git commit -m "Description claire"
git push
```

Éviter d'utiliser :

```bash
git add .
```

sans avoir préalablement vérifié `git status`.

---

# 33. Fichiers et données à ne jamais versionner

Ne jamais envoyer sur GitHub :

```text
.env
.venv/
mot de passe PostgreSQL
BREVO_API_KEY
SECRET_KEY
tokens
clés privées
identifiants personnels
```

En cas de doute :

```bash
git status
```

---

# 34. Redémarrer son environnement les jours suivants

Il n'est pas nécessaire de refaire toute l'installation.

À chaque nouvelle session :

```bash
cd ~/dev/campus-request-skolae
source .venv/bin/activate
```

Vérification facultative :

```bash
python --version
which python
```

Puis :

```bash
git status
git pull
```

et :

```bash
flask run
```

Si de nouvelles migrations ont été ajoutées depuis le dernier `git pull` :

```bash
flask db upgrade
```

---

# 35. Diagnostic rapide en cas de problème

## `ModuleNotFoundError: No module named 'sqlalchemy'`

Vérifier :

```bash
which python
which flask
```

Ils doivent pointer vers :

```text
.../campus-request-skolae/.venv/...
```

Puis :

```bash
python -m pip install -r requirements.txt
```

---

## `PyYAML ... is not supported on this platform`

Vérifier :

```bash
python --version
```

Si l'environnement utilise Python 3.14 alors que la configuration de référence du projet est Python 3.13, recréer le `.venv` avec Python 3.13.

---

## `Either SQLALCHEMY_DATABASE_URI or SQLALCHEMY_BINDS must be set`

Vérifier :

```bash
ls -la .env*
```

Puis :

```bash
python -c "from config import Config; print(bool(Config.SQLALCHEMY_DATABASE_URI))"
```

Si cela affiche :

```text
False
```

vérifier `DATABASE_URL` dans `.env`.

---

## PostgreSQL refuse la connexion

Tester indépendamment de Flask :

```bash
psql -h localhost -U <USER> -d campus_request
```

Puis vérifier :

```bash
sudo systemctl status postgresql
```

---

## Flask utilise le Python système

Si :

```bash
which flask
```

renvoie :

```text
/usr/bin/flask
```

le `.venv` n'est probablement pas actif.

Faire :

```bash
source .venv/bin/activate
```

Puis :

```bash
which flask
```

---

## `.venv` existe mais n'est pas un dossier

Vérifier :

```bash
ls -ld .venv
```

Si `.venv` est un fichier vide :

```bash
rm .venv
python3.13 -m venv .venv
```

---

# 36. Checklist d'installation complète

Une nouvelle personne doit pouvoir valider toutes ces cases avant de commencer à développer.

## Git

- [ ] repository cloné ;
- [ ] bon `origin` ;
- [ ] `main` récupéré ;
- [ ] branche personnelle créée.

## Python

- [ ] Python 3.13 installé ;
- [ ] `.venv` créé avec Python 3.13 ;
- [ ] `.venv` activé ;
- [ ] `which python` pointe vers `.venv` ;
- [ ] `which flask` pointe vers `.venv`.

## Dépendances

- [ ] `requirements.txt` installé ;
- [ ] `pip check` sans erreur ;
- [ ] Flask importable ;
- [ ] SQLAlchemy importable ;
- [ ] Flask-Migrate importable.

## PostgreSQL

- [ ] PostgreSQL installé ;
- [ ] service actif ;
- [ ] utilisateur local créé ;
- [ ] base `campus_request` créée ;
- [ ] connexion `psql` fonctionnelle.

## Configuration

- [ ] `.env` créé ;
- [ ] `DATABASE_URL` configurée ;
- [ ] `SECRET_KEY` configurée ;
- [ ] `.env` ignoré par Git.

## Flask

- [ ] `flask --app app routes` fonctionne ;
- [ ] migrations appliquées ;
- [ ] `flask db current` est au `head` ;
- [ ] `flask run` fonctionne ;
- [ ] site accessible dans le navigateur.

## Brevo

- [ ] `BREVO_API_KEY` configurée ;
- [ ] `SMTP_SENDER` configuré ;
- [ ] expéditeur autorisé côté Brevo ;
- [ ] `BASE_URL` correcte ;
- [ ] email de confirmation réellement reçu.

## Fonctionnel

- [ ] inscription ;
- [ ] confirmation ;
- [ ] connexion ;
- [ ] création ticket ;
- [ ] consultation admin ;
- [ ] changement de statut ;
- [ ] réorientation ;
- [ ] historique étudiant.

---

# 37. Parcours applicatif à comprendre avant de développer

```text
INSCRIPTION
     ↓
CONFIRMATION EMAIL
     ↓
CONNEXION
     ↓
DASHBOARD ÉTUDIANT
     ↓
CRÉATION TICKET
     ↓
CLASSIFICATION
     ↓
ROUTAGE
     ↓
MODÉRATION
     ↓
DASHBOARD ADMIN
     ↓
TRAITEMENT / RÉORIENTATION
     ↓
MISE À JOUR DU STATUT
     ↓
HISTORIQUE ÉTUDIANT
```

Une nouvelle fonctionnalité ne doit pas casser ce parcours.

---

# 38. Règle générale

Avant de modifier Campus Request :

```text
1. environnement fonctionnel
2. base fonctionnelle
3. migrations à jour
4. tests existants verts
5. branche personnelle
6. développement
7. nouveaux tests
8. test manuel
9. revue
10. intégration
```

Ne pas modifier le code pour contourner un problème d'installation locale.

Il faut d'abord déterminer si le problème vient :

```text
Python
   ↓
venv
   ↓
dépendances
   ↓
.env
   ↓
PostgreSQL
   ↓
migrations
   ↓
Flask
   ↓
application
```

Cette méthode permet de diagnostiquer l'environnement sans introduire de modifications inutiles dans le projet.
