from sqlalchemy import create_engine

INITIAL_MIGRATION = [
    """
        CREATE TABLE IF NOT EXISTS teachers(
            name VARCHAR(100) PRIMARY KEY 
        );
    """,
    """               
    CREATE TABLE IF NOT EXISTS groups(
        group_name VARCHAR(80) PRIMARY KEY
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS subjects(
        subject_name VARCHAR(80) PRIMARY KEY,
        is_lecture BOOLEAN
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS classrooms(
        classroom_name VARCHAR(80) PRIMARY KEY,
        is_for_lecture BOOLEAN
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS teacher_to_subject(
        name VARCHAR(100),
        subject_name VARCHAR(100),
        FOREIGN KEY(name) REFERENCES teachers(name),
        FOREIGN KEY(subject_name) REFERENCES subjects(subject_name) ,
        PRIMARY KEY (name, subject_name)
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS group_to_subject(
        group_name VARCHAR(100),
        subject_name VARCHAR(100),
        number_of_hours INTEGER,
        FOREIGN KEY(group_name) REFERENCES groups(group_name),
        FOREIGN KEY(subject_name) REFERENCES subjects(subject_name) ,
        PRIMARY KEY (group_name, subject_name)
    );
    """
]


db = create_engine('sqlite:///main.db')

for query in INITIAL_MIGRATION:
    db.execute(query)
