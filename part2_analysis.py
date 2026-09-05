import sqlite3
import os

import pandas as pd

#my CellFrequency table is already completed, so just query it and export as a csv in output folde.r 
def main():
    project_dir = os.path.dirname(os.path.abspath(__file__))
    database_path = os.path.join(project_dir, "databaseSchema.db")
    output_dir = os.path.join(project_dir, "outputAnswers")
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "part2_CellFrequency.csv")

    with sqlite3.connect(database_path) as conn:

        query = ("""
                SELECT * FROM CellFrequency; 
                """)
        df = pd.read_sql_query(query, conn)
        df.to_csv(output_path, index=False)

if __name__ == "__main__":
    main()    