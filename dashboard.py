import os
import re
import sqlite3

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import streamlit as st
from plantuml import PlantUML


PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE_PATH = os.path.join(PROJECT_DIR, "databaseSchema.db")
OUTPUT_DIR = os.path.join(PROJECT_DIR, "outputAnswers")
PLANTUML_SERVER = "https://www.plantuml.com/plantuml/svg/"
POPULATIONS = ["b_cell", "cd8_t_cell", "cd4_t_cell", "nk_cell", "monocyte"]

SCHEMA_PLANTUML = """
@startuml
left to right direction
skinparam backgroundColor transparent
skinparam shadowing false
skinparam defaultFontSize 10
skinparam entity {
    BackgroundColor #F8FBFD
    BorderColor #1F526D
    FontColor #163B4D
}
entity Subject {
    * subject : TEXT <<PK>>
    --
    condition : TEXT
    age : INTEGER
    sex : TEXT
    project : TEXT
}
entity Treatment {
    * treatment_id : INTEGER <<PK, AUTOINCREMENT>>
    --
    subject : TEXT <<FK>>
    treatment : TEXT
    response : TEXT
}
entity Sample {
    * sample : TEXT <<PK>>
    --
    subject : TEXT <<FK>>
    sample_type : TEXT
    time_from_treatment_start : INTEGER
}
entity CellFrequency {
    * sample : TEXT <<PK, FK>>
    * population : TEXT <<PK>>
    --
    percentage : DECIMAL
    count : INTEGER
    total_count : INTEGER
}
Subject ||--o{ Treatment : has
Subject ||--o{ Sample : has
Sample ||--o{ CellFrequency : has
@enduml
"""

st.set_page_config(
    page_title="Teiko Technical | Immune Response",
    layout="wide",
)

st.markdown(
    """
    <style>
    .block-container { padding-top: 1.1rem; padding-bottom: 1rem; }
    h1 { color: #163b4d; margin-bottom: 0.1rem !important; }
    h2, h3 { color: #1f526d; margin-top: 0.55rem !important; }
    [data-testid="stMetricValue"] { color: #1f526d; }
    [data-testid="stMetric"] { border: 1px solid #d8e2e8; padding: 0.6rem; border-radius: 6px; background: #f8fbfd; }
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_data
def read_sql(query):
    with sqlite3.connect(DATABASE_PATH) as connection:
        return pd.read_sql_query(query, connection)


@st.cache_data
def read_csv(filename):
    return pd.read_csv(os.path.join(OUTPUT_DIR, filename))


@st.cache_data
def read_metrics():
    metrics_path = os.path.join(OUTPUT_DIR, "part3_LogisticRegressionMetrics.txt")
    with open(metrics_path, encoding="utf-8") as metrics_file:
        return metrics_file.read()


def metric_value(metrics_text, label):
    match = re.search(rf"{re.escape(label)}: ([0-9.]+)", metrics_text)
    return match.group(1) if match else "N/A"


def load_part3_data():
    return read_sql(
        """
        SELECT cf.sample, Sample.subject, cf.population, cf.percentage,
               cf.count, cf.total_count, Sample.time_from_treatment_start,
               Treatment.response
        FROM CellFrequency AS cf
        INNER JOIN Sample ON cf.sample = Sample.sample
        INNER JOIN Subject ON Sample.subject = Subject.subject
        INNER JOIN Treatment ON Subject.subject = Treatment.subject
        WHERE Treatment.treatment = 'miraclib'
          AND Subject.condition = 'melanoma'
          AND Sample.sample_type = 'PBMC'
        """
    )


def load_male_average():
    result = read_sql(
        """
        SELECT ROUND(AVG(cf.count), 2) AS avg_b_cell_count
        FROM CellFrequency AS cf
        INNER JOIN Sample ON cf.sample = Sample.sample
        INNER JOIN Subject ON Sample.subject = Subject.subject
        INNER JOIN Treatment ON Subject.subject = Treatment.subject
        WHERE cf.population = 'b_cell'
          AND Subject.condition = 'melanoma'
          AND Subject.sex = 'M'
          AND Sample.time_from_treatment_start = 0
          AND Treatment.response = 'yes'
        """
    )
    return result.iloc[0]["avg_b_cell_count"]


def render_boxplots(dataframe, selected_population):
    plot_data = dataframe.copy()
    plot_data["time_from_treatment_start"] = plot_data["time_from_treatment_start"].astype(str)
    populations = POPULATIONS if selected_population == "All populations" else [selected_population]
    figure, axes = plt.subplots(
        1,
        len(populations),
        figsize=(16 if len(populations) > 1 else 7, 3.7),
        sharey=True,
        squeeze=False,
    )
    axes = axes[0]
    for axis, population in zip(axes, populations):
        population_data = plot_data[plot_data["population"] == population]
        sns.boxplot(
            data=population_data,
            x="time_from_treatment_start",
            y="percentage",
            hue="response",
            palette={"yes": "#1f7a8c", "no": "#e07a5f"},
            linewidth=0.8,
            ax=axis,
        )
        axis.set_title(population.replace("_", " ").title())
        axis.set_xlabel("Time from treatment start (days)")
        axis.set_ylabel("Relative frequency (%)")
        axis.set_ylim(0, 50)
        axis.grid(axis="y", alpha=0.2)
        if axis != axes[0] and axis.get_legend() is not None:
            axis.get_legend().remove()
    axes[0].legend(title="Response", loc="upper right")
    figure.tight_layout()
    st.pyplot(figure, use_container_width=True)
    plt.close(figure)


def schema_tab():
    st.subheader("Relational schema")
    st.caption("SQLite design used by Part 1: patient metadata connects to treatments and samples, which connect to cell frequencies.")
    try:
        svg = PlantUML(url=PLANTUML_SERVER).processes(SCHEMA_PLANTUML).decode("utf-8")
        st.components.v1.html(svg, height=280, scrolling=False)
    except Exception:
        st.warning("The PlantUML service is unavailable. The schema is still defined in load_data.py and databaseSchema.db.")


def explorer_tab():
    st.subheader("Part 2: relative frequency explorer")
    st.caption("Each row represents one immune-cell population in one biological sample.")
    table = st.selectbox("Database table", ["Subject", "Treatment", "Sample", "CellFrequency"], key="database_table")
    table_data = read_sql(f'SELECT * FROM "{table}"')
    st.dataframe(table_data, use_container_width=True, height=285, hide_index=True)


def findings_tab():
    part3_data = load_part3_data()
    evidence = read_csv("part3_statisticalEvidence.csv")
    coefficients = read_csv("part3_LogisticRegressionCoefs.csv")
    metrics_text = read_metrics()
    male_average = load_male_average()

    st.subheader("Study scope")
    st.caption("Melanoma patients | miraclib treatment | PBMC samples | responder versus non-responder")

    metric_columns = st.columns(4)
    metric_columns[0].metric("Patients analyzed", metric_value(metrics_text, "Patients analyzed"))
    metric_columns[1].metric("Cross-validated ROC AUC", metric_value(metrics_text, "Cross-validated ROC AUC"))
    metric_columns[2].metric("Cross-validated accuracy", metric_value(metrics_text, "Cross-validated accuracy"))
    metric_columns[3].metric("Male responder B-cell average", f"{male_average:,.2f}")

    significant = evidence[evidence["significant"] == True]
    if not significant.empty:
        finding = significant.iloc[0]
        st.success(
            f"Primary finding: {finding['population']} at day {int(finding['time_from_treatment_start'])} "
            f"was higher in responders (median {finding['median_yes_percentage']:.2f}%) than non-responders "
            f"(median {finding['median_no_percentage']:.2f}%). Holm-adjusted p-value: "
            f"{finding['adjusted_p_value']:.4f}."
        )
    st.info("Interpretation: the model is close to chance performance, so these results support an association rather than a reliable response prediction model.")

    st.subheader("Part 3: responder comparison")
    st.caption("Use the population dropdown to view all five cell types together or focus on one population.")
    population_choice = st.selectbox("Population view", ["All populations"] + POPULATIONS, key="population_view")
    render_boxplots(part3_data, population_choice)

    evidence_column, coefficient_column = st.columns(2)
    with evidence_column:
        st.markdown("**Statistical evidence**")
        st.caption("Hypothesis Testing of Findings and p-value")
        evidence_display = evidence.copy()
        evidence_display["significant"] = evidence_display["significant"].map({True: "Yes", False: "No"})
        st.dataframe(evidence_display, use_container_width=True, height=220, hide_index=True)
    with coefficient_column:
        st.markdown("**Largest logistic-regression coefficients**")
        st.caption("The top-two coefficients of magnitude represent original findings")
        st.dataframe(coefficients, use_container_width=True, height=220, hide_index=True)

    with st.expander("Model metrics"):
        st.code(metrics_text)


def query_tab():
    st.subheader("Part 4: targeted SQL questions")
    st.caption("The headline answer uses melanoma males, responders, baseline samples, and all sample/treatment types.")
    answer = read_csv("part4_avgNumberB_Cells.csv")
    st.metric("Average B-cell count", f"{answer.iloc[0]['avg_b_cell_count']:,.2f}")

    query_files = {
        "Baseline melanoma PBMC miraclib samples": "part4_query1.csv",
        "Baseline records by project": "part4_query2-1.csv",
        "Baseline records by response": "part4_query2-2.csv",
        "Baseline records by sex": "part4_query2-3.csv",
        "Male melanoma responder B-cell average": "part4_avgNumberB_Cells.csv",
    }
    selected_query = st.selectbox("Query output", list(query_files), key="query_output")
    st.dataframe(read_csv(query_files[selected_query]), use_container_width=True, height=350, hide_index=True)


def main():
    st.title("Teiko Technical: Immune Response Dashboard")
    st.caption("A findings-first view of the SQLite data model, cell-frequency analysis, response statistics, and targeted queries.")

    tabs = st.tabs(["Findings", "Part 4 queries", "Data explorer", "Database schema"])
    with tabs[0]:
        findings_tab()
    with tabs[1]:
        query_tab()
    with tabs[2]:
        explorer_tab()
    with tabs[3]:
        schema_tab()


if __name__ == "__main__":
    main()
