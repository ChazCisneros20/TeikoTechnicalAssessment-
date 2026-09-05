import os
import sqlite3
import pandas as pd


def main():
    project_dir = os.path.dirname(os.path.abspath(__file__))
    database_path = os.path.join(project_dir, 'databaseSchema.db')
    output_dir = os.path.join(project_dir, 'outputAnswers')
    os.makedirs(output_dir, exist_ok=True)

    with sqlite3.connect(database_path) as conn:
        query1 = (
            """
            SELECT cf.sample, Sample.subject, cf.population, cf.percentage, cf.count, cf.total_count,
                   Sample.time_from_treatment_start, Treatment.response
            FROM CellFrequency cf
            INNER JOIN Sample ON cf.sample = Sample.sample
            INNER JOIN Subject ON Sample.subject = Subject.subject
            INNER JOIN Treatment ON Subject.subject = Treatment.subject
            WHERE Treatment.treatment = 'miraclib'
              AND Subject.condition = 'melanoma'
              AND Sample.sample_type = 'PBMC'
              AND Sample.time_from_treatment_start = 0;
            """
        )
        query2 = (
            """
            SELECT Subject.project, COUNT(*) AS record_count
            FROM CellFrequency cf
            INNER JOIN Sample ON cf.sample = Sample.sample
            INNER JOIN Subject ON Sample.subject = Subject.subject
            INNER JOIN Treatment ON Subject.subject = Treatment.subject
            WHERE Treatment.treatment = 'miraclib'
              AND Subject.condition = 'melanoma'
              AND Sample.sample_type = 'PBMC'
              AND Sample.time_from_treatment_start = 0
            GROUP BY Subject.project;
            """
        )
        query3 = (
            """
            SELECT Treatment.response, COUNT(*) AS record_count
            FROM CellFrequency cf
            INNER JOIN Sample ON cf.sample = Sample.sample
            INNER JOIN Subject ON Sample.subject = Subject.subject
            INNER JOIN Treatment ON Subject.subject = Treatment.subject
            WHERE Treatment.treatment = 'miraclib'
              AND Subject.condition = 'melanoma'
              AND Sample.sample_type = 'PBMC'
              AND Sample.time_from_treatment_start = 0
            GROUP BY Treatment.response;
            """
        )
        query4 = (
            """
            SELECT Subject.sex, COUNT(*) AS record_count
            FROM CellFrequency cf
            INNER JOIN Sample ON cf.sample = Sample.sample
            INNER JOIN Subject ON Sample.subject = Subject.subject
            INNER JOIN Treatment ON Subject.subject = Treatment.subject
            WHERE Treatment.treatment = 'miraclib'
              AND Subject.condition = 'melanoma'
              AND Sample.sample_type = 'PBMC'
              AND Sample.time_from_treatment_start = 0
            GROUP BY Subject.sex;
            """
        )
        query5 = (
            """
            SELECT ROUND(AVG(cf.count), 2) AS avg_b_cell_count
            FROM CellFrequency cf
            INNER JOIN Sample ON cf.sample = Sample.sample
            INNER JOIN Subject ON Sample.subject = Subject.subject
            INNER JOIN Treatment ON Subject.subject = Treatment.subject
            WHERE cf.population = 'b_cell'
              AND Subject.condition = 'melanoma'
              AND Sample.time_from_treatment_start = 0
              AND Treatment.response = 'yes';
            """
        )

        q1 = pd.read_sql_query(query1, conn)
        q2 = pd.read_sql_query(query2, conn)
        q3 = pd.read_sql_query(query3, conn)
        q4 = pd.read_sql_query(query4, conn)
        q5 = pd.read_sql_query(query5, conn)

    q1.to_csv(os.path.join(output_dir, 'part4_query1.csv'), index=False)
    q2.to_csv(os.path.join(output_dir, 'part4_query2-1.csv'), index=False)
    q3.to_csv(os.path.join(output_dir, 'part4_query2-2.csv'), index=False)
    q4.to_csv(os.path.join(output_dir, 'part4_query2-3.csv'), index=False)
    q5.to_csv(os.path.join(output_dir, 'part4_avgNumberB_Cells.csv'), index=False)


if __name__ == "__main__":
    main()