import sqlite3
import pandas as pd 

df = pd.read_csv('cell-count.csv')

with sqlite3.connect('databaseSchema.db') as conn:
    curr = conn.cursor()
    #=== Create `Subject` table. === 
    query = """
    CREATE TABLE IF NOT EXISTS Subject(
        subject_id INTEGER PRIMARY KEY AUTOINCREMENT, 
        subject TEXT UNIQUE NOT NULL, 
        condition NOT NULL, 
        age INTEGER NOT NULL, 
        sex TEXT NOT NULL, 
        project TEXT NOT NULL
    );
    """
    curr.execute(query)
    #=== CREATE `Sample` table. ============================
    query = """
    CREATE TABLE IF NOT EXISTS Sample(
        sample_id INTEGER PRIMARY KEY AUTOINCREMENT, 
        subject_id INTEGER,
        sample TEXT UNIQUE NOT NULL, 
        sample_type TEXT NOT NULL, 
        FOREIGN KEY (subject_id) REFERENCES Subject(subject_id)
    );
    """
    curr.execute(query)
    #=== CREATE `Treatment` table. ==================
    query = """
    CREATE TABLE IF NOT EXISTS Treatment(
        treatment_id INTEGER PRIMARY KEY AUTOINCREMENT, 
        subject_id INTEGER NOT NULL,
        treatment TEXT NOT NULL, 
        response TEXT NULL,
        FOREIGN KEY (subject_id) REFERENCES Subject(subject_id)
    
    );
    """
    #===INSERT INTO `Subject` Table =================
    df[['subject', 'condition', 'project', 'age', 'sex']][::3].to_sql('Subject', conn, index=False, if_exists='fail')


    #===INSERT INTO `Treatment` Table ================
    
    # (subject : subject_id) EX: {sbj000 : 0}
    curr.execute("""SELECT subject, subject_id FROM Subject;""")

    #the subject dict will be as {sbj001 : 1}... 
    subject_dict = dict(curr.fetchall())

    for row in df[::3].iterrows():
                    #subject_dict['sbj000']
        subject_id = subject_dict[row['subject']]

        curr.execute(
            f"""
            INSERT INTO Treatment(subject_id, treatment, response) VALUES({subject_id}, {row['treatment']}, {row['response']});
            """)

    #=== INSERT INTO `Sample` Table ======================
    for row in df.itterows():
        print('Stopped')
        
    
        
        

    



    #===Final Close===
    curr.close()
    conn.close()

