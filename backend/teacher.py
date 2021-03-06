import config
import backend.crypt
from flask import Blueprint, render_template, abort, make_response, request, redirect, url_for, g
from jinja2 import TemplateNotFound

teacher_page = Blueprint('teacher_page', __name__, template_folder='templates')

@teacher_page.route('/account/teacher', methods=['GET', 'POST'])
def teacher():
    token = request.cookies.get('jwt')

    if token is None:
        return redirect(url_for('login_page.login'))
    
    decoded_token = backend.crypt.decode_jwt(token)
    type = decoded_token['type']
    uid = decoded_token['uid']
    name = decoded_token['first_name']

    if not type == 'professor':
        return redirect(url_for('login_page.login'))

    mycursor = config.mydb.cursor()

    mycursor.execute(f"SELECT * FROM Position pos INNER JOIN User user ON pos.professor = user.uid WHERE professor={uid}")

    positionResult = mycursor.fetchall()
    labels = ('pid', 'professor', 'course', 'description', 'location', 'startTime', 'endTime', 'uid', 'fname', 'lname', 'email')
    positions = []
    for position in positionResult:
        positions.append(dict(map(lambda x,y: (x, y), labels, position)))


    for position in positions:
        labels = ('aid', 'uid', 'major', 'gpa', 'essay', 'resume', 'firstPick', 'secondPick', 'thirdPick', 'uid', 'fname', 'lname', 'email')
        mycursor = config.mydb.cursor()

        mycursor.execute(f"SELECT * FROM `Application` app INNER JOIN User user ON app.uid=user.uid WHERE app.firstPick={position['pid']}")

        firstPickResults = mycursor.fetchall()

        firstPicks = []
        for firstPick in firstPickResults:
            firstPicks.append(dict(map(lambda x,y: (x, y), labels, firstPick)))

        mycursor = config.mydb.cursor()

        mycursor.execute(f"SELECT * FROM `Application` app INNER JOIN User user ON app.uid=user.uid WHERE app.secondPick={position['pid']}")

        secondPickResults = mycursor.fetchall()

        secondPicks = []
        for secondPick in secondPickResults:
            secondPicks.append(dict(map(lambda x,y: (x, y), labels, secondPick)))

        mycursor = config.mydb.cursor()

        mycursor.execute(f"SELECT * FROM `Application` app INNER JOIN User user ON app.uid=user.uid WHERE app.thirdPick={position['pid']}")

        thirdPickResults = mycursor.fetchall()

        thirdPicks = []
        for thirdPick in thirdPickResults:
            thirdPicks.append(dict(map(lambda x,y: (x, y), labels, thirdPick)))

        position['students'] = firstPicks + secondPicks + thirdPicks

    return render_template('teacher.html', name=name, positions=positions)

@teacher_page.route('/account/position', methods=['GET', 'POST'])
def position():
    token = request.cookies.get('jwt')

    if token is None:
        return redirect(url_for('login_page.login'))
    
    decoded_token = backend.crypt.decode_jwt(token)
    type = decoded_token['type']

    if not type == 'professor':
        return redirect(url_for('login_page.login'))

    name = decoded_token['first_name']
    uid = decoded_token['uid']

    if request.method == 'POST':
        subject = request.form['cname']
        course = request.form['cnum']
        description = request.form['description']
        location = request.form['location']
        startTime = request.form['startTime']
        endTime = request.form['endTime']

        mycursor = config.mydb.cursor()

        sql = "INSERT INTO Position (professor, course, description, location, startTime, endTime) VALUES (%s, %s, %s, %s, %s, %s)"
        val = (uid, subject + course, description, location, startTime, endTime)
        mycursor.execute(sql, val)

        config.mydb.commit()

        return redirect(url_for('teacher_page.teacher'))

    return render_template('position.html', name=name)
