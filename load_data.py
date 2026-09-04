import sqlite3
import pandas as pd

df = pd.read_csv('cell-count.csv')



with sqlite3.connection('databaseSchema.db') as conn:
    curr = conn.cursor()

    #=== CREATE TABLES ======
    curr.execute(
        """
        CREATE TABLE IF NOT EXISTS Subject(
            subject TEXT PRIMARY KEY, 
            condition TEXT NOT NULL,
            age INTEGER NOT NULL CHECK age > 0,
            sex TEXT NOT NULL, 
            project TEXT NOT NULL 
        );
        CREATE TABLE IF NOT EXISTS Treatment(
            treatment_id INTEGER PRIMARY KEY AUTOINCREMENT, 
            subject TEXT NOT NULL,
            treatment TEXT NOT NULL,
            response TEXT NULL,
            FOREIGN KEY (subject) REFERENCES Subject(subject)
        );
        CREATE TABLE IF NOT EXISTS Sample(
            sample TEXT PRIMARY KEY AUTOINCREMENT, 
            subject INTEGER NOT NULL, 
            sample_type TEXT NOT NULL, 
            time_from_treatment_start TEXT NOT NULL CHECK time_from_treatment_start >= 0,
            FOREIGN KEY (subject) REFERENCES Subject(subject)
        );
        CREATE TABLE IF NOT EXISTS CellFrequency(
            sample TEXT NOT NULL, 
            population TEXT NOT NULL, 
            percentage DECIMAL NOT NULL, 
            count INTEGER NOT NULL, 
            total_count INTEGER NOT NULL
            PRIMARY KEY (sample, population),
            FOREIGN KEY (sample) REFERENCES Sample(sample)
        );
        """

    )
    for useless_index, row in df[::3].iterrows():
        curr.execute(
            f""""
            INSERT INTO Subject(subject, condition, age, sex, project) VALUES
            (
                {row['subject']}, {row['condition']}, {row['age']}, {row['sex']}, {row['project']}  
            );
            INSERT INTO Treatment(subject, treatment, response) VALUES
            (
                {row['subject']}, {row['treatment']}, {row['response']}
            );
            """
        )
    for useless_index, row in df.iterrows():
        curr.execute(
            
        )
    


    

    

    