
from flask import Flask, render_template, redirect, session, request, url_for, flash
import pymongo

db_client = pymongo.MongoClient("mongodb://localhost:27017")

app = Flask(__name__)

app.secret_key = 'super secret key'

db = db_client["student"]
collection = db['student']
faculty = db['faculty']
course = db['course']
addedCourse = db['addedCourse']
portalAdmin = db['portalAdmin']


@app.route('/s_login', methods=['GET', "POST"])
def s_login():
    if request.method == "POST":
        stuid = request.form['stu_Id']
        password = request.form['stu_password']
        user = collection.find_one({'student_id': stuid})

        if user and user['password'] == password:
            # Authentication successful, set session variables
            session['email'] = user['email']
            session['name'] = user['name']
            session['student_id'] = user['student_id']

            # Redirect to dashboard or profile page
            return redirect(url_for('s_homepage'))
        else:
            # Authentication failed, show error message
            error_message = "Invalid email or password"
            return render_template("student-login.html", error_message=error_message)

    return render_template("student-login.html")


@app.route('/facultyLogin', methods=['GET', "POST"])
def faculty_login():
    if request.method == "POST":
        facultyemail = request.form['fac_email']
        password = request.form['fac_password']
        user = faculty.find_one({'email': facultyemail})

        if user and user['password'] == password:
            # Authentication successful, set session variables
            session['email'] = user['email']
            session['name'] = user['name']
            session['faculty_department'] = user['faculty_department']

            # Redirect to dashboard or profile page
            return redirect(url_for('f_homepage'))
        else:
            # Authentication failed, show error message
            error_message = "Invalid email or password"
            return render_template("faculty-login.html", error_message=error_message)

    return render_template("faculty-login.html")


@app.route('/adminLogin', methods=['GET', "POST"])
def admin_login():
    if request.method == "POST":
        adm_name = request.form['adm_name']
        adm_password = request.form['adm_password']
        user = portalAdmin.find_one({'name': adm_name})

        if user and user['password'] == adm_password:
            # Authentication successful, set session variables
            session['name'] = user['name']

            # Redirect to dashboard or profile page
            return redirect(url_for('admin'))
        else:
            # Authentication failed, show error message
            error_message = "Invalid email or password"
            return render_template("admin-login.html", error_message=error_message)

    return render_template("admin-login.html")


@app.route('/addCourse', methods=['GET', "POST"])
def add_course():
    if request.method == "POST":
        c_code = request.form['course_code']
        c_name = request.form['course_name']
        c_description = request.form['course_description']
        c_seat = request.form['course_seat']
        c_credit = request.form['course_credit']

        print(c_code, c_name, c_description, c_seat, c_credit)

        course.insert_one(
            {
                'Course Code': c_code,
                'Course Name': c_name,
                'Course Description': c_description,
                'Course Seat': c_seat,
                'Course Credit': c_credit,
                'Added by': session['name'],
                'Course Department': session['faculty_department']
            }
        )
        print("course add successfully")
        return render_template("addCourse.html", **locals())
    # username = session["name"]

    return render_template("addCourse.html", **locals())


@app.route('/facultyHomepage', methods=['GET', "POST"])
def f_homepage():
    if request.method == "POST":
        return render_template("facultyHomepage.html", **locals())
    # username = session["name"]

    return render_template("facultyHomepage.html", **locals())


@app.route('/homepage', methods=['GET', "POST"])
def s_homepage():
    if request.method == "POST":
        return render_template("homepage.html", **locals())
    # username = session["name"]

    return render_template("homepage.html", **locals())


@app.route('/advising', methods=['GET', "POST"])
def advising():
    course_data = course.find()
    query = {"Added by": session['name']}

    added_course_data = addedCourse.find(query)

    if request.method == "POST":

        if 'submit-row' in request.form:
            # Get the document ID of the submitted row
            document_id = request.form['document-id']

            # Retrieve the values for the submitted row
            c_code = request.form.get(f'course-code-{document_id}')
            c_name = request.form.get(f'course-name-{document_id}')
            c_credit = request.form.get(f'course-credit-{document_id}')
            c_seat = request.form.get(f'course-seat-{document_id}')
            c_faculty = request.form.get(f'added-by-{document_id}')

            # Perform the database operation for the specific row
            # Update the values in the MongoDB database

            print(c_code, c_name, c_faculty, c_seat, c_credit)

            addedCourse.insert_one(
                {
                    'Student': session['student_id'],
                    'Course Code': c_code,
                    'Course Name': c_name,
                    'Course Credit': c_credit,
                    'Added by': session['name'],
                    'Faculty': c_faculty

                }
            )

        if 'drop-row' in request.form:
            print("drop Clicked")
            document_id = request.form['document-id']
            print(document_id)

            c_code = request.form.get(f'course-taken-code-{document_id}')

            # Perform the database operation for the specific row
            # Update the values in the MongoDB database

            # Retrieve the values for the submitted row

            que = {"Course Code": c_code}
            addedCourse.delete_one(que)

            # Retrieve the course data and render the template
            course_data = course.find()
            query = {"Added by": session['name']}
            added_course_data = addedCourse.find(query)
            return render_template("advising.html", table_data=course_data, course_taken=added_course_data)

        return render_template("advising.html", table_data=course_data, course_taken=added_course_data)

    return render_template("advising.html", **locals(), table_data=course_data, course_taken=added_course_data)


@app.route('/signUp', methods=['GET', "POST"])
def signup():
    if request.method == "POST":
        name = request.form['inputName']
        email = request.form['inputEmail']
        stuid = request.form['inputID']
        phone = request.form['phone']
        department = request.form['selected-department']
        dob = request.form['dob']
        address = request.form['address']
        cgpa = request.form['cgpa']
        if request.form['inputPassword'] == request.form['inputConfirmPassword']:
            password = request.form['inputPassword']

            result = collection.find({'student_id': 'stuid'})
            print(result, name, email, stuid, password)

            collection.insert_one(
                {
                    'name': name,
                    'email': email,
                    'student_id': stuid,
                    'password': password,
                    'phone': phone,
                    'department': department,
                    'date of birth': dob,
                    'address': address,
                    'cgpa': cgpa
                }
            )

            print("added")
            flash('Student added successfully!', 'success')
            return render_template("admin.html")
            # print("not added")

        flash('Username already exists!', 'error')
        return redirect(url_for('signup'))
    # collection.insert_one({'name': 'John Doe', 'email': 'johndoe@example.com'})
    return render_template("signUp.html", **locals())


@app.route('/facultySignUp', methods=['GET', "POST"])
def facultysignup():
    if request.method == "POST":
        name = request.form['inputName']
        email = request.form['inputEmail']
        facultydepartment = request.form['selected-department']
        if request.form['inputPassword'] == request.form['inputConfirmPassword']:
            password = request.form['inputPassword']

            print(name, email, facultydepartment, password)

            faculty.insert_one(
                {
                    'name': name,
                    'email': email,
                    'faculty_department': facultydepartment,
                    'password': password
                }
            )
            print("added")
            flash('Student added successfully!', 'success')
            return render_template("admin.html")
        print("not added")

        flash('Username already exists!', 'error')
        return redirect(url_for('facultysignup'))
    # collection.insert_one({'name': 'John Doe', 'email': 'johndoe@example.com'})
    return render_template("facultySignUp.html", **locals())


@app.route('/profile', methods=['GET', "POST"])
def s_profile():
    course_data = collection.find()
    query = {"studnet_id": session['student_id']}
    student_data = collection.find(query)

    if request.method == "POST":
        return render_template("profile.html", **locals())

    return render_template("profile.html", table_data=student_data)


@app.route('/admin', methods=['GET', "POST"])
def admin():
    if request.method == 'POST':
        if 'submit-fac' in request.form:
            return render_template("student-login.html", **locals())
        if 'submit-stu' in request.form:
            return render_template("faculty-login.html", **locals())
        if 'submit-course' in request.form:
            return render_template("faculty-login.html", **locals())

    return render_template("admin.html", **locals())


@app.route('/', methods=['GET', "POST"])
def index():
    session.clear()
    if request.method == 'POST':
        if 'submit-stu' in request.form:
            print("stu")
            return render_template("student-login.html", **locals())
        if 'submit-fac' in request.form:
            return render_template("faculty-login.html", **locals())
        if 'submit-adm' in request.form:
            return render_template("admin-login.html", **locals())
    return render_template("index.html", **locals())


if __name__ == "__main__":
    app.run(host='127.0.0.1', port=5002)
