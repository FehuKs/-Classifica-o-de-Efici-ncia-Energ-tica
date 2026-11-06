"""Aquisição e contrato dos dados, independente do treinamento."""
from pathlib import Path

import numpy as np
import pandas as pd

FEATURES = tuple(f"X{i}" for i in range(1, 9))


class DataAccessError(RuntimeError):
    """Falha de acesso ao conjunto de dados externo."""


def validate_data(features: pd.DataFrame, targets: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    missing = set(FEATURES) - set(features.columns)
    if missing or "Y1" not in targets.columns:
        raise ValueError("Dados devem conter X1 a X8 e o alvo Y1.")
    if not features.columns.is_unique or not targets.columns.is_unique:
        raise ValueError("Nomes de colunas devem ser únicos.")
    if len(features) < 10 or len(features) != len(targets) or not features.index.equals(targets.index):
        raise ValueError("Atributos e alvos devem ter índices alinhados e ao menos 10 linhas.")
    x = features.loc[:, list(FEATURES)].copy()
    y = targets.loc[:, ["Y1"]].copy()
    for frame in (x, y):
        if any(not pd.api.types.is_numeric_dtype(dtype) or pd.api.types.is_bool_dtype(dtype)
               for dtype in frame.dtypes):
            raise ValueError("Atributos e alvo devem ser numéricos.")
        if not np.isfinite(frame.to_numpy(dtype=float)).all():
            raise ValueError("Dados não podem conter valores ausentes ou infinitos.")
    if y.Y1.nunique() < 2:
        raise ValueError("Y1 deve conter valores distintos para classificação.")
    return x, y


def load_data(csv_path: str | Path | None = None) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Lê CSV local ou a fonte oficial. Sem fallback silencioso para dados sintéticos."""
    if csv_path is not None:
        frame = pd.read_csv(csv_path)
        return validate_data(frame, frame)
    from ucimlrepo import fetch_ucirepo
    try:
        dataset = fetch_ucirepo(id=242)
    except (ConnectionError, OSError, ValueError) as exc:
        raise DataAccessError(
            "Não foi possível obter UCI 242. Verifique acesso HTTPS a archive.ics.uci.edu "
            "ou informe --data com um CSV local contendo X1 a X8 e Y1."
        ) from exc
    return validate_data(dataset.data.features, dataset.data.targets)
