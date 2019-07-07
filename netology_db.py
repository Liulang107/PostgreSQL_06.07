import psycopg2


def create_db():  # создает таблицы
    sql_create_students_table = "CREATE TABLE IF NOT EXISTS student (" \
                                "id serial PRIMARY KEY, " \
                                "name varchar(100) NOT NULL, " \
                                "gpa numeric(10, 2), " \
                                "birth timestamp with time zone" \
                                ");"

    sql_create_courses_table = "CREATE TABLE IF NOT EXISTS course (" \
                               "id serial PRIMARY KEY, " \
                               "name varchar(100) NOT NULL" \
                               ");"

    sql_create_student_course_table = "CREATE TABLE IF NOT EXISTS student_course (" \
                                      "id serial PRIMARY KEY, " \
                                      "student_id INTEGER REFERENCES student(id), " \
                                      "course_id INTEGER REFERENCES course(id)" \
                                      ");"

    cur.execute(sql_create_students_table)
    cur.execute(sql_create_courses_table)
    cur.execute(sql_create_student_course_table)


def get_students(course_id):  # возвращает студентов определенного курса
    cur.execute("SELECT student.name FROM student_course "
                "JOIN student ON student_course.student_id = student.id "
                "JOIN course ON student_course.course_id = course.id "
                "WHERE course_id = %s", (course_id,))
    return cur.fetchall()


def add_students(course_name, students):  # создает студентов и записывает их на курс
    cur.execute("INSERT INTO course (name) VALUES (%s) RETURNING id", (course_name,))
    id_of_new_course = cur.fetchone()[0]
    for student in students:
        cur.execute("INSERT INTO student (name, gpa, birth) VALUES (%s, %s, %s) RETURNING id AS id_of_new_student",
                    (student["name"], student["gpa"], student["birth"]))
        id_of_new_student = cur.fetchone()[0]
        cur.execute("INSERT INTO student_course (student_id, course_id) VALUES (%s, %s)",
                    (id_of_new_student, id_of_new_course))


def add_student(student):  # создает студента
    cur.execute("INSERT INTO student (name, gpa, birth) VALUES (%s, %s, %s)",
                (student["name"], student["gpa"], student["birth"]))


def get_student(student_id):
    cur.execute("SELECT name, gpa, birth FROM student WHERE id = %s", (student_id,))
    return cur.fetchall()


def work_with_netology_database():
    """
    gs – (get students) – команда, которая спросит id курса и отобразит имена студентов на курсе;
    as – (add students) – команда, которая спросит данные студентов в формате: "Василий Гупкин; 5;
    1991-10-10|<данные следующего студента>", и спросит имя курса и добавит студентов на курс;
    a – (add student) – команда, которая спросит данные студентов в формате: "Василий Гупкин; 3.5;
    1991-10-10", - и добавит в список студентов;
    g – (get student) – команда, которая спросит id студента и отобразит данные о нем;
    q - (quit) - команда, которая завершает выполнение программы
    """
    print(
        "Вас приветствует программа помошник!\n"
        "(Введите help, для просмотра списка поддерживаемых команд)\n"
    )
    while True:
        user_command = input("Введите команду: ")

        if user_command == "gs":
            user_course_id = input("Введите id курса: ")
            students_of_course = get_students(user_course_id)
            if students_of_course:
                print("Имена студентов на курсе: ")
                for student in students_of_course:
                    print(student[0])
            else:
                print("На данном курсе нет студентов")

        elif user_command == "as":
            user_course_name = input("Введите имя курса: ")
            user_students = input("Введите список студентов: ")
            students = []
            if '|' in user_students:
                student_list = user_students.split('|')
            else:
                student_list = [user_students, ]
            for student in student_list:
                student_data = student.split('; ')
                student_dict = {"name": student_data[0], "gpa": float(student_data[1]), "birth": student_data[2]}
                students.append(student_dict)
            add_students(user_course_name, students)
            print("Студенты добавлены на курс '{}'".format(user_course_name))

        elif user_command == "a":
            user_student = input("Введите данные студента: ")
            student_data = user_student.split('; ')
            student_dict = {"name": student_data[0], "gpa": float(student_data[1]), "birth": student_data[2]}
            add_student(student_dict)
            print("Студент {} добавлен в список".format(student_dict["name"], ))

        elif user_command == "g":
            user_student_id = input("Введите id студента: ")
            student_data = get_student(user_student_id)
            if student_data:
                print("Данные студента c id {}: ".format(user_student_id))
                for data in student_data[0]:
                    print(str(data))
            else:
                print("Студент не найден")

        elif user_command == "help":
            print(work_with_netology_database().__doc__)

        elif user_command == "q":
            break


if __name__ == "__main__":
    with psycopg2.connect("dbname=netology_db user=netology_user") as conn:
        with conn.cursor() as cur:
            create_db()
            work_with_netology_database()
