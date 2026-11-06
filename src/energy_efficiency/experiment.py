"""Protocolo original: mediana global, holdout 70/30 e três classificadores."""
from dataclasses import dataclass
from time import perf_counter
from typing import Any

import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.tree import DecisionTreeClassifier

from .data import validate_data

CLASS_NAMES = ["Alta Eficiência (0)", "Baixa Eficiência (1)"]


@dataclass
class Experiment:
    threshold: float
    features: pd.DataFrame
    labels: pd.Series
    x_train: pd.DataFrame
    x_test: pd.DataFrame
    y_train: pd.Series
    y_test: pd.Series
    models: dict[str, Any]
    results: dict[str, dict[str, Any]]


def binarize(target: pd.Series) -> tuple[pd.Series, float]:
    threshold = float(target.median())
    return (target > threshold).astype(int), threshold


def run_experiment(features: pd.DataFrame, targets: pd.DataFrame) -> Experiment:
    x, targets = validate_data(features, targets)
    y, threshold = binarize(targets.Y1)
    # Mantém a definição retrospectiva original; não é avaliação prospectiva.
    x_train, x_test, y_train, y_test = train_test_split(
        x, y, test_size=0.3, shuffle=True, random_state=42
    )
    if set(y_train) != {0, 1} or set(y_test) != {0, 1}:
        raise ValueError("O holdout original precisa de ambas as classes no treino e no teste.")
    models = {
        "Árvore de Decisão": DecisionTreeClassifier(criterion="entropy", max_depth=4, random_state=42),
        "KNN (K=5)": make_pipeline(StandardScaler(), KNeighborsClassifier(n_neighbors=5)),
        "Regressão Logística": make_pipeline(StandardScaler(), LogisticRegression(max_iter=1000, random_state=42)),
    }
    results = {}
    for name, model in models.items():
        start = perf_counter()
        model.fit(x_train, y_train)
        elapsed = perf_counter() - start
        predicted = model.predict(x_test)
        results[name] = {
            "training_seconds": elapsed,
            "report": classification_report(y_test, predicted, labels=[0, 1],
                                            target_names=CLASS_NAMES, output_dict=True, zero_division=0),
        }
    return Experiment(threshold, x, y, x_train, x_test, y_train, y_test, models, results)


def comparison(experiment: Experiment) -> pd.DataFrame:
    return pd.DataFrame([
        {"modelo": name, "accuracy": result["report"]["accuracy"],
         **{key: result["report"]["macro avg"][key] for key in ("precision", "recall", "f1-score")},
         "training_seconds": result["training_seconds"]}
        for name, result in experiment.results.items()
    ]).set_index("modelo")
