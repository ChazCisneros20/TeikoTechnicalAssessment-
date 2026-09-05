import sqlite3
import os
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from scipy.stats import mannwhitneyu
from statsmodels.stats.multitest import multipletests
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix, roc_auc_score
from sklearn.model_selection import StratifiedKFold, cross_val_predict
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

def main():
    project_dir = os.path.dirname(os.path.abspath(__file__))
    database_path = os.path.join(project_dir, 'databaseSchema.db')
    output_dir = os.path.join(project_dir, 'outputAnswers')
    os.makedirs(output_dir, exist_ok=True)
    image_path = os.path.join(output_dir, 'part3BoxPlots.png')

    with sqlite3.connect(database_path) as conn:
        curr = conn.cursor()
        df = pd.read_sql_query('''SELECT cf.sample, Sample.subject, cf.population, cf.percentage, cf.count, cf.total_count, 
        Sample.time_from_treatment_start, Treatment.response FROM CellFrequency cf 
        INNER JOIN Sample ON cf.sample = Sample.sample 
        INNER JOIN Subject ON Sample.subject = Subject.subject 
        INNER JOIN Treatment ON Subject.subject = Treatment.subject 
        WHERE Treatment.treatment = "miraclib" AND Subject.condition = "melanoma" AND Sample.sample_type = "PBMC";''', conn)
    conn.close()

    # ------------------------------------------------------------------
    # Boxplot section
    # ------------------------------------------------------------------
    populations = ["b_cell", "cd8_t_cell", "cd4_t_cell", "nk_cell", "monocyte"]

    fig, axes = plt.subplots(1, 5, figsize=(25, 5), sharey=True)
    for axis, population in zip(axes, populations):
        sns.boxplot(data=df[df["population"] == population], x="time_from_treatment_start", y="percentage", hue="response", palette="Set1", ax=axis)
        axis.set_title(population)
        axis.set_xlabel("Weeks")
        axis.set_ylim(0, 50)
        axis.set_ylabel("Relative Frequency (%)")
        if population in {"cd4_t_cell", "nk_cell"}:
            for spine in axis.spines.values():
                spine.set_visible(True)
                spine.set_color("black")
                spine.set_linewidth(2.5)
            annotation_text = (
                "higher cd4_t_cells may result in treatment responses"
                if population == "cd4_t_cell"
                else "initially higher count at the start, then at 7-14 a lower count results in treatment response"
            )
            axis.annotate(annotation_text, xy=(0.5, 0.97), xycoords="axes fraction", ha="center", va="top", fontsize=9, color="navy", bbox=dict(boxstyle="round,pad=0.35", facecolor="gold", edgecolor="black", linewidth=1.5, alpha=0.9))
        if axis != axes[0]:
            axis.get_legend().remove()
    axes[0].legend(title="Response")
    fig.suptitle("Cell Population Relative Frequencies by Treatment Response", fontsize=16)
    plt.tight_layout()
    plt.savefig(image_path, dpi=300, bbox_inches='tight')
    plt.close(fig)

    # ------------------------------------------------------------------
    # Additional single-population claim plots
    # ------------------------------------------------------------------
    for population, filename in [("cd4_t_cell", "part3_firstClaim.png"), ("nk_cell", "part3_secondClaim.png")]:
        fig_single, ax = plt.subplots(figsize=(8, 5), sharey=True)
        sns.boxplot(data=df[df["population"] == population], x="time_from_treatment_start", y="percentage", hue="response", palette="Set1", ax=ax)
        ax.set_title(population)
        ax.set_xlabel("Weeks")
        ax.set_ylim(0, 50)
        ax.set_ylabel("Relative Frequency (%)")
        for spine in ax.spines.values():
            spine.set_visible(True)
            spine.set_color("black")
            spine.set_linewidth(2.5)
        annotation_text = (
            "higher cd4_t_cells may result in treatment responses"
            if population == "cd4_t_cell"
            else "initially higher count at the start, then at 7-14 a lower count results in treatment response"
        )
        ax.annotate(annotation_text, xy=(0.5, 0.97), xycoords="axes fraction", ha="center", va="top", fontsize=10, color="navy", bbox=dict(boxstyle="round,pad=0.35", facecolor="gold", edgecolor="black", linewidth=1.5, alpha=0.9))
        ax.legend(title="Response")
        fig_single.suptitle(f"{population} Treatment Response Pattern", fontsize=14)
        plt.tight_layout()
        plt.savefig(os.path.join(output_dir, filename), dpi=300, bbox_inches='tight')
        plt.close(fig_single)

    # ------------------------------------------------------------------
    # Logistic regression section
    # ------------------------------------------------------------------
    model_df = df[["subject", "response", "population", "percentage", "time_from_treatment_start"]].copy()
    model_df["time_from_treatment_start"] = model_df["time_from_treatment_start"].astype(int)
    populations = ["b_cell", "cd8_t_cell", "cd4_t_cell", "nk_cell", "monocyte"]
    feature_table = model_df.pivot_table(index=["subject", "response"], columns=["population", "time_from_treatment_start"], values="percentage", aggfunc="first")
    feature_table.columns = [f"{population}_day{time}" for population, time in feature_table.columns]
    feature_table = feature_table.reset_index()
    feature_table["response"] = (feature_table["response"] == "yes").astype(int)
    for population in populations:
        feature_table[f"{population}_change_14_minus_0"] = feature_table[f"{population}_day14"] - feature_table[f"{population}_day0"]
    feature_columns = [column for column in feature_table.columns if column not in ["subject", "response"]]
    X = feature_table[feature_columns]
    y = feature_table["response"]
    model = Pipeline([("scaler", StandardScaler()), ("classifier", LogisticRegression(max_iter=2000))])
    folds = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    predicted_probabilities = cross_val_predict(model, X, y, cv=folds, method="predict_proba")[:, 1]
    predicted_labels = predicted_probabilities >= 0.5
    # ------------------------------------------------------------------
    # Metrics section
    # ------------------------------------------------------------------
    metrics_text = (
        f"Patients analyzed: {len(feature_table)}\n"
        f"Cross-validated ROC AUC: {roc_auc_score(y, predicted_probabilities):.3f}\n"
        f"Cross-validated accuracy: {accuracy_score(y, predicted_labels):.3f}\n"
        "Confusion matrix [rows=actual, columns=predicted]:\n"
        f"{confusion_matrix(y, predicted_labels)}\n"
        f"{classification_report(y, predicted_labels, target_names=['no', 'yes'])}\n"
    )
    metrics_path = os.path.join(output_dir, 'part3_LogisticRegressionMetrics.txt')
    with open(metrics_path, 'w', encoding='utf-8') as f:
        f.write(metrics_text)
    model.fit(X, y)
    coefficient_table = pd.DataFrame({"feature": feature_columns, "coefficient": model.named_steps["classifier"].coef_[0]})
    coefficient_table["absolute_coefficient"] = coefficient_table["coefficient"].abs()
    coefficient_table = coefficient_table.sort_values("absolute_coefficient", ascending=False).head(15)
    coef_path = os.path.join(output_dir, 'part3_LogisticRegressionCoefs.csv')
    coefficient_table.to_csv(coef_path, index=False)

    analysis_df = df[["response", "population", "percentage", "time_from_treatment_start"]].copy()
    analysis_df["time_from_treatment_start"] = analysis_df["time_from_treatment_start"].astype(int)
    feature_tests = [
        {"feature": "cd4_t_cell_day7", "population": "cd4_t_cell", "alternative": "greater", "claim": "Higher CD4 day 7 percentage is associated with yes response"},
        {"feature": "nk_cell_day7", "population": "nk_cell", "alternative": "less", "claim": "Lower NK day 7 percentage is associated with yes response"},
    ]
    evidence_rows = []
    for test in feature_tests:
        feature_data = analysis_df[(analysis_df["population"] == test["population"]) & (analysis_df["time_from_treatment_start"] == 7)]
        yes_values = feature_data.loc[feature_data["response"] == "yes", "percentage"]
        no_values = feature_data.loc[feature_data["response"] == "no", "percentage"]
        u_statistic, p_value = mannwhitneyu(yes_values, no_values, alternative=test["alternative"])
        evidence_rows.append({
            "feature": test["feature"],
            "claim": test["claim"],
            "population": test["population"],
            "time_from_treatment_start": 7,
            "n_yes": len(yes_values),
            "n_no": len(no_values),
            "median_yes_percentage": yes_values.median(),
            "median_no_percentage": no_values.median(),
            "median_difference_yes_minus_no": yes_values.median() - no_values.median(),
            "u_statistic": u_statistic,
            "p_value": p_value,
        })
    evidence_df = pd.DataFrame(evidence_rows)
    evidence_df["adjusted_p_value"] = multipletests(evidence_df["p_value"], method="holm")[1]
    evidence_df["significant"] = evidence_df["adjusted_p_value"] < 0.05
    evidence_df = evidence_df[["feature", "claim", "population", "time_from_treatment_start", "n_yes", "n_no", "median_yes_percentage", "median_no_percentage", "median_difference_yes_minus_no", "u_statistic", "p_value", "adjusted_p_value", "significant"]]
    evidence_path = os.path.join(output_dir, 'part3_statisticalEvidence.csv')
    evidence_df.to_csv(evidence_path, index=False)
    

if __name__ == "__main__":
    main()