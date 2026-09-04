import sqlite3
import pandas as pd

df = pd.read_csv('cell-count.csv')



with sqlite3.connect('databaseSchema.db') as conn:
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
            sample TEXT PRIMARY KEY, 
            subject TEXT NOT NULL, 
            sample_type TEXT NOT NULL, 
            time_from_treatment_start TEXT NOT NULL CHECK time_from_treatment_start >= 0,
            FOREIGN KEY (subject) REFERENCES Subject(subject)
        );
        CREATE TABLE IF NOT EXISTS CellFrequency(
            sample TEXT NOT NULL, 
            population TEXT NOT NULL, 
            percentage DECIMAL NOT NULL, 
            count INTEGER NOT NULL, 
            total_count INTEGER NOT NULL,
            PRIMARY KEY (sample, population),
            FOREIGN KEY (sample) REFERENCES Sample(sample)
        );
        """

    )
    i=0
    for useless_index, row in df.iterrows():
        if i % 3 == 0:
            curr.execute(
                f"""
                INSERT INTO Subject(subject, condition, age, sex, project) VALUES
                (
                    "{row['subject']}", "{row['condition']}", {row['age']}, "{row['sex']}", "{row['project']}"  
                );
                """
            )
            curr.execute(
                f"""
                INSERT INTO Treatment(subject, treatment, response) VALUES
                (
                    "{row['subject']}", "{row['treatment']}", "{row['response']}"
                );
                """
            )
        curr.execute(
            f""""
            INSERT INTO Sample(sample, subject, sample_type, time_from_treatment_start) VALUES
            (
                "{row['sample']}", "{row['subject']}", "{row['sample_type']}", {row['time_from_treatment_start']}
            );
            """
        )
        i+=1
    for uslsindx, row in df.iterrows():
        populations = ['b_cell', 'cd8_t_cell', 'cd4_t_cell', 'nk_cell', 'monocyte']
        totalCount = 0
        for i in range(5):
            totalCount += row[populations[i]]
        for i in range(5):
            #this should create 5 rows based on the 3 sample records in the original csv.
            curr.execute(
                f"""
                INSERT INTO CellFrequency(sample, population, percentage, count, total_count) VALUES
                (
                    {row['sample']}, {populations[i]}, {row[populations[i]] / totalCount}, {row[populations[i]]}, {totalCount}
                )
                """
            )
    


    

    

    