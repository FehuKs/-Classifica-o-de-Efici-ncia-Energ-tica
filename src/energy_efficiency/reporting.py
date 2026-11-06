"""Artefatos de apresentação derivados dos resultados, sem alterar os modelos."""
import json
from importlib.metadata import version
from pathlib import Path

import matplotlib.pyplot as plt
from sklearn.metrics import ConfusionMatrixDisplay
from sklearn.tree import plot_tree

from .experiment import CLASS_NAMES, Experiment, comparison


def save_reports(experiment: Experiment, output: str | Path, *, source: str) -> Path:
    directory = Path(output)
    directory.mkdir(parents=True, exist_ok=True)
    table = comparison(experiment)
    payload = {
        "protocol": {"threshold": experiment.threshold, "threshold_scope": "full_dataset",
                     "test_size": 0.3, "random_state": 42, "stratified": False},
        "source": source, "rows": len(experiment.features),
        "train_rows": len(experiment.x_train), "test_rows": len(experiment.x_test),
        "versions": {name: version(name) for name in ("numpy", "pandas", "scikit-learn", "matplotlib", "ucimlrepo")},
        "results": experiment.results,
    }
    (directory / "metrics.json").write_text(json.dumps(payload, indent=2, ensure_ascii=False, allow_nan=False), encoding="utf-8")
    table.to_csv(directory / "comparison.csv")

    def save(fig, name):
        try:
            fig.tight_layout()
            fig.savefig(directory / name, dpi=150, bbox_inches="tight")
        finally:
            plt.close(fig)

    fig, axes = plt.subplots(2, 4, figsize=(16, 8))
    for ax, column in zip(axes.flat, experiment.features.columns):
        ax.hist(experiment.features[column], bins=15, edgecolor="white")
        ax.set_title(column)
    save(fig, "histogramas_atributos.png")
    fig, ax = plt.subplots(figsize=(5, 4))
    experiment.features.X5.value_counts().sort_index().plot.bar(ax=ax)
    ax.set(title="Distribuição de X5 — Altura total", ylabel="Instâncias")
    save(fig, "atributo_x5.png")
    fig, ax = plt.subplots(figsize=(5, 4))
    counts = experiment.labels.value_counts().sort_index()
    ax.bar(CLASS_NAMES, counts.values)
    for i, count in enumerate(counts):
        ax.text(i, count, f"{count} ({count / counts.sum():.1%})", ha="center", va="bottom")
    ax.margins(y=0.15)
    save(fig, "distribuicao_classes.png")
    for i, (name, model) in enumerate(experiment.models.items(), 1):
        fig, ax = plt.subplots(figsize=(6, 5))
        ConfusionMatrixDisplay.from_estimator(model, experiment.x_test, experiment.y_test,
                                             display_labels=CLASS_NAMES, cmap="Blues", ax=ax)
        ax.set_title(name)
        save(fig, f"confusion_matrix_{i}.png")
    fig, ax = plt.subplots(figsize=(20, 10))
    plot_tree(experiment.models["Árvore de Decisão"], feature_names=list(experiment.features.columns),
              class_names=CLASS_NAMES, filled=True, rounded=True, fontsize=10, ax=ax)
    save(fig, "arvore_decisao.png")
    return directory
