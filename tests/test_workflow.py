"""Dados sintéticos exclusivos de teste; não representam resultados da UCI."""
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.tree import DecisionTreeClassifier

from energy_efficiency.data import DataAccessError, FEATURES, load_data, validate_data
from energy_efficiency.experiment import binarize, comparison, run_experiment
from energy_efficiency.reporting import save_reports


def fixture():
    rng = np.random.default_rng(42)
    x = pd.DataFrame(rng.normal(size=(120, 8)), columns=FEATURES)
    y = pd.DataFrame({"Y1": 10 * x.X1 + x.X2})
    return x, y


class DataTests(unittest.TestCase):
    def test_boundary_belongs_to_class_zero(self):
        labels, threshold = binarize(pd.Series([1, 2, 2, 3, 4]))
        self.assertEqual(threshold, 2)
        self.assertEqual(labels.tolist(), [0, 0, 0, 1, 1])

    def test_invalid_inputs(self):
        x, y = fixture()
        for invalid in (x.drop(columns="X1"), x.assign(X1=np.nan),
                        x.assign(X1=np.inf), x.assign(X1="text")):
            with self.subTest(columns=list(invalid.columns)), self.assertRaises(ValueError):
                validate_data(invalid, y)
        with self.assertRaises(ValueError):
            validate_data(x, y.set_axis(range(1, len(y) + 1)))
        with self.assertRaises(ValueError):
            validate_data(x, y.assign(Y1=1))

    def test_local_csv_and_column_order(self):
        x, y = fixture()
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "data.csv"
            pd.concat([y, x.loc[:, list(reversed(FEATURES))]], axis=1).to_csv(path, index=False)
            loaded_x, loaded_y = load_data(path)
            self.assertEqual(tuple(loaded_x.columns), FEATURES)
            np.testing.assert_allclose(loaded_x, x)
            np.testing.assert_allclose(loaded_y, y)

    def test_uci_failure_is_actionable(self):
        with patch("ucimlrepo.fetch_ucirepo", side_effect=ConnectionError("unavailable")):
            with self.assertRaisesRegex(DataAccessError, "--data"):
                load_data()

    def test_uci_success_contract(self):
        from types import SimpleNamespace
        x, y = fixture()
        dataset = SimpleNamespace(data=SimpleNamespace(features=x, targets=y))
        with patch("ucimlrepo.fetch_ucirepo", return_value=dataset) as fetch:
            actual_x, actual_y = load_data()
        fetch.assert_called_once_with(id=242)
        pd.testing.assert_frame_equal(actual_x, x)
        pd.testing.assert_frame_equal(actual_y, y)


class ExperimentTests(unittest.TestCase):
    def test_predictions_match_original_protocol(self):
        x, y = fixture()
        result = run_experiment(x, y)
        labels = (y.Y1 > y.Y1.median()).astype(int)
        train, test, train_y, test_y = train_test_split(x, labels, test_size=.3, shuffle=True, random_state=42)
        scaler = StandardScaler().fit(train)
        original = [
            (DecisionTreeClassifier(criterion="entropy", max_depth=4, random_state=42), train, test),
            (KNeighborsClassifier(n_neighbors=5), scaler.transform(train), scaler.transform(test)),
            (LogisticRegression(max_iter=1000, random_state=42), scaler.transform(train), scaler.transform(test)),
        ]
        for (name, model), (reference, fit_x, predict_x) in zip(result.models.items(), original):
            reference.fit(fit_x, train_y)
            np.testing.assert_array_equal(model.predict(result.x_test), reference.predict(predict_x))
            self.assertEqual(result.results[name]["report"]["accuracy"], accuracy_score(test_y, model.predict(test)))
        for model in list(result.models.values())[1:]:
            np.testing.assert_allclose(model[0].mean_, train.mean())
            self.assertFalse(np.allclose(model[0].mean_, x.mean()))

    def test_reports_and_graphs(self):
        x, y = fixture()
        result = run_experiment(x, y)
        with TemporaryDirectory() as tmp:
            for _ in range(2):  # Atualização dos artefatos deve ser repetível.
                directory = save_reports(result, tmp, source="synthetic_test")
            payload = json.loads((directory / "metrics.json").read_text())
            self.assertEqual(payload["rows"], 120)
            self.assertEqual(payload["train_rows"], 84)
            self.assertEqual(payload["protocol"]["threshold"], float(y.Y1.median()))
            self.assertEqual(payload["results"], result.results)
            self.assertEqual(len(list(directory.glob("*.png"))), 7)
            for image in directory.glob("*.png"):
                self.assertGreater(image.stat().st_size, 1000)
            table = pd.read_csv(directory / "comparison.csv", index_col="modelo")
            np.testing.assert_allclose(table.accuracy, comparison(result).accuracy)


class CliTests(unittest.TestCase):
    def test_local_cli_and_invalid_input_exit_status(self):
        import os
        import subprocess
        import sys
        x, y = fixture()
        with TemporaryDirectory() as tmp:
            csv = Path(tmp) / "input.csv"
            output = Path(tmp) / "reports"
            pd.concat([x, y], axis=1).to_csv(csv, index=False)
            result = subprocess.run([sys.executable, "-m", "energy_efficiency", "--data", str(csv),
                                     "--output", str(output)], capture_output=True, text=True,
                                    env={**os.environ, "MPLBACKEND": "Agg"}, timeout=60)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("Regressão Logística", result.stdout)
            self.assertTrue((output / "metrics.json").is_file())
            invalid = subprocess.run([sys.executable, "-m", "energy_efficiency", "--data", str(csv)+".missing"],
                                     capture_output=True, text=True, timeout=30)
            self.assertEqual(invalid.returncode, 1)
            self.assertIn("ERROR:", invalid.stderr)
            self.assertNotIn("Traceback", invalid.stderr)
