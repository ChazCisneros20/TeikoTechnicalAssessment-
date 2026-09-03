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
    #=== Create `Sample` table. === 
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
    #=== Create `Treatment` table. === 
    query = """
    CREATE TABLE IF NOT EXISTS Treatment(
        treatment_id INTEGER PRIMARY KEY AUTOINCREMENT, 
        subject_id INTEGER NOT NULL,
        treatment TEXT NOT NULL, 
        response TEXT NULL,
        FOREIGN KEY (subject_id) REFERENCES Subject(subject_id)
    
    );
    """
    #Each `Subject` entity has 3 instances/rows of repeated data. let's take the repeated data as one row/instance. 
    #Start from index 0, step of 3, to get the 1st out of 3 subject rows. 
    df[['subject', 'condition', 'project', 'age', 'sex']][::3].to_sql('Subject', conn, index=False, if_exists='fail')
    
    query = """
    SELECT subject_id FROM Subject; 
    """
    curr.execute(query)
    #the subject dict will be as 
    subject_dict = dict(curr.fetchall())
    for subject_id in zip(curr.fetchall(), df['treatment', 'response'][::3]):
        query = f"""
                INSERT INTO Treatment(subject_id, treatment, response) VALUES({subject_id}, )
                """
        
        

    



    #===Final Close===
    curr.close()
    conn.close()

