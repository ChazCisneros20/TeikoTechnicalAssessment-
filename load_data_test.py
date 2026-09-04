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
        time_from_treatment_start INT NOT NULL 
        CHECK (
            time_from_treatment_start = 0 
            OR time_from_treatment_start = 7 OR time_from_treatment_start = 14
        ), 
        b_cell INT NOT NULL, 
        cd8_t_cell INT NOT NULL CHECK (cd8_t_cell >= 0), 
        cd4_t_cell INT NOT NULL CHECK (cd4_t_cell >= 0), 
        nk_cell INT NOT NULL CHECK (nk_cell >= 0), 
        monocyte INT NOT NULL CHECK (monocyte >= 0), 
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
    curr.execute(query)
    #===INSERT INTO `Subject` Table =================
    df[['subject', 'condition', 'project', 'age', 'sex']][::3].to_sql('Subject', conn, index=False, if_exists='append')


    #===INSERT INTO `Treatment` Table ================
    
    # (subject : subject_id) EX: {sbj000 : 0}
    curr.execute("""SELECT subject, subject_id FROM Subject;""")

    #the subject dict will be as {sbj001 : 1}... 
    subject_dict = dict(curr.fetchall())

    #We are unpacking index, but not using it. we want to iterate the series 
    for index, row in df[::3].iterrows():
                    #subject_dict['sbj000']
        #Reuse logic later for `Sample` Table.
        subject_id = subject_dict[row['subject']]

        curr.execute(
            f"""
            INSERT INTO Treatment(subject_id, treatment, response) VALUES({subject_id}, "{row['treatment']}", "{row['response']}" );
            """)

    #=== INSERT INTO `Sample` Table ======================
    for useless_index, row in df.iterrows():
        subject_id = subject_dict[row['subject']]
        curr.execute(
            f"""
            INSERT INTO Sample(subject_id, sample, sample_type, time_from_treatment_start, b_cell, cd8_t_cell, cd4_t_cell, nk_cell, monocyte) 
            VALUES({subject_id}, "{row['sample']}", "{row['sample_type']}", {row['time_from_treatment_start']}, {row['b_cell']}, {row['cd8_t_cell']}, {row['cd4_t_cell']}, {row['nk_cell']}, {row['monocyte']});
            """)


    #=== CREATE `CellFrequency` Table =====================
    curr.execute("""
        CREATE TABLE IF NOT EXISTS CellFrequency(
            sample_id INT NOT NULL,
            population TEXT NOT NULL, 
            count INT NOT NULL,
            percentage FLOAT NOT NULL, 
            totalCount INT NOT NULL, 
            PRIMARY KEY (sample_id, population),
            FOREIGN KEY(sample_id) REFERENCES Sample(sample_id)
            );
        """
                 )
    curr.execute("""SELECT sample_id FROM Sample;""")
    sample_ids = curr.fetchall()
    j = 0 
    #Multiply all 10500 x 5 = 52000 rows 
    for useless_index, row in df.iterrows():
        cellTypes = ['b_cell', 'cd8_t_cell', 'cd4_t_cell', 'nk_cell', 'monocyte']

        count=0
        for i in range(5):
            count+=row[cellTypes[i]]

        for i in range(5):

            curr.execute(
                f"""
                INSERT INTO CellFrequency(sample_id, population, count, percentage, totalCount) VALUES 
                ({sample_ids[j][0]}, "{cellTypes[i]}", {row[cellTypes[i]]}, {row[cellTypes[i]] / count * 100}, {count});
                """
            )

        j+=1

    
    

        
    
        
        

    





