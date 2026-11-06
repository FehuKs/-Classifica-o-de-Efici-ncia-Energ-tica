"""Interface de execução do mesmo experimento apresentado no notebook."""
import argparse
import logging

from .data import DataAccessError, load_data
from .experiment import comparison, run_experiment
from .reporting import save_reports


def main() -> int:
    parser = argparse.ArgumentParser(description="Classificação relativa de carga de aquecimento — UCI 242")
    parser.add_argument("--data", help="CSV local com X1 a X8 e Y1; padrão: API UCI")
    parser.add_argument("--output", default="artifacts", help="Diretório para relatórios (arquivos existentes serão atualizados)")
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    try:
        x, y = load_data(args.data)
        experiment = run_experiment(x, y)
        directory = save_reports(experiment, args.output, source="local_csv" if args.data else "uci:242")
    except (DataAccessError, OSError, ValueError) as exc:
        logging.error("%s", exc)
        return 1
    print(comparison(experiment).to_string())
    logging.info("Relatórios gravados em %s", directory)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
