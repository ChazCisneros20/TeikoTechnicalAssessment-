## ERD / Schema Diagram. How it scales and supports analytics 

The current Schema Diagram has taken the original `cell-count.csv` and converted it into 4 different entity relations. 
1. `Subject`: Contains:
- `subject` P.K. 
- `condition` 
- `age` 
- `sex` 
- `project` 


`Subject` and `Treatment` have a 1:1 relationship where one Subject has *one* Treatment record. 
`Subject` and `Sample` have a 1:N relationship 


## Setup and usage

Run the full data pipeline, including dependency installation:

```bash
make pipeline
```

After the pipeline finishes, start the Streamlit dashboard:

```bash
make dashboard
```

The pipeline creates or refreshes `databaseSchema.db` and regenerates the files in `outputAnswers/`.