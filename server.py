from flask import Flask, request, jsonify
from setting import *
from utils import allowed_file
from database import Database, pre_define_db
import evaluators
from inspect import getmembers, isfunction
from werkzeug.utils import secure_filename
import pandas as pd

app = Flask(__name__)
app.secret_key = APP_SECRET_KEY

pre_define_db()


def fetch_leader_board(db: Database, competition_id):
    db.query(f"""
        select * from leader_board where competition_id = {competition_id} order by score, created_at;
    """)
    result = db.fetchall()

    return [
        dict(zip(Database.leader_board_cols, res)) for res in result
    ]


@app.route('/')
def home():
    return 'welcome'


# create competition
@app.route('/competitions', methods=['POST'])
def create_competition():
    body = request.form

    if body.get('secret') != COMPETITION_SECRET_KEY:
        return jsonify(
            success=False,
            message='it\'s safe enough :]'
        )

    evaluators_list = [fun[0] for fun in getmembers(evaluators, isfunction)]
    if body.get('evaluator') not in evaluators_list:
        return jsonify(
            success=False,
            message='invalid evaluator passed'
        )

    if body.get('title') is None or len(body.get('title')) < 1:
        return jsonify(
            success=False,
            message='invalid title'
        )

    db = Database()
    db.query(f"""select * from competitions where title = '{body.get('title')}';""")
    if db.fetchone():
        return jsonify(
            success=False,
            message='competition title already exists, please choose another one'
        )

    file = request.files.get('file')
    if 'file' not in request.files or file.filename == '':
        return jsonify(
            success=False,
            message='no file attached'
        )

    if not allowed_file(file.filename):
        return jsonify(
            success=False,
            message='file ext. is not valid'
        )

    # TODO: check competition file head columns
    # df_evaluation = pd.read_csv(file)
    # if 'id' not in df_evaluation.columns or 'value' not in df_evaluation.columns:
    #     return jsonify(
    #         success=False,
    #         message='we need `id` and `value` in file head'
    #     )

    competition_dir = os.path.join(COMPETITION_FOLDER, body.get('title'))
    os.mkdir(competition_dir)

    file_name = secure_filename(file.filename)
    file_path = os.path.join(competition_dir, file_name)
    file.save(file_path)

    db.query(f"""
        insert into competitions(title, evaluation_file_path, evaluator)
            values('{body.get('title')}', '{file_path}', '{body.get('evaluator')}');
    """)
    db.commit()

    db.query(f"""select * from competitions where title = '{body.get('title')}';""")
    result = db.fetchone()

    data = dict(zip(Database.competition_cols, result))
    return jsonify(
        success=True,
        message='competition created successfully',
        data=data
    )


# competitions list
@app.route('/competitions')
def competition_list():
    db = Database()
    db.query(f"""select * from competitions;""")
    result = db.fetchall()

    data = [
        dict(zip(Database.competition_cols, res)) for res in result
    ]
    return jsonify(
        success=True,
        data=data
    )


# send an answer to specific competition
@app.route('/competitions/<int:_id>/send-answer', methods=['POST'])
def send_answer(_id):
    body = request.form

    if body.get('name') is None:
        return jsonify(
            success=False,
            message='we love to know your name :]'
        )

    db = Database()
    db.query(f"""select * from competitions where id = {_id};""")
    result = db.fetchone()
    if not result:
        return jsonify(
            success=False,
            message='competition not found'
        )

    competition = dict(zip(Database.competition_cols, result))
    evaluator = getattr(evaluators, competition['evaluator'])

    file = request.files.get('file')
    if 'file' not in request.files or file.filename == '':
        return jsonify(
            success=False,
            message='no file attached'
        )

    if not allowed_file(file.filename):
        return jsonify(
            success=False,
            message='file ext. is not valid'
        )

    df_answer = pd.read_csv(file)
    if 'id' not in df_answer.columns or 'answer' not in df_answer.columns:
        return jsonify(
            success=False,
            message='we need `id` and `answer` in file head'
        )

    df_evaluation = pd.read_csv(competition.get('evaluation_file_path'))
    df_final = pd.merge(df_evaluation, df_answer, on='id', how='left')

    score = evaluator(df_final['value'], df_final['answer'])

    db.query(f"""
        insert into leader_board(competition_id, name, score)
            values({competition.get('id')}, '{body.get('name')}', {score});
    """)
    db.commit()

    data = fetch_leader_board(db, competition['id'])

    return jsonify(
        success=True,
        message='competition created successfully',
        data=data
    )


# to retrieve leader board
@app.route('/leader_board/<int:competition_id>')
def leader_board(competition_id):
    db = Database()
    return jsonify(
        success=True,
        data=fetch_leader_board(db, competition_id)
    )
