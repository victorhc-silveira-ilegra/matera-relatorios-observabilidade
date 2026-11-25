from __future__ import annotations

import argparse
import logging
import sys
from datetime import date, datetime
from pathlib import Path

from app.application.use_cases import (
    GenerateFlagshipReportCommand,
    GenerateFlagshipReportUseCase,
    GenerateRevolutReportCommand,
    GenerateRevolutReportUseCase,
)
from app.domain.time_window import (
    BRT,
    WINDOW_ORDER,
    build_time_window,
    detect_current_window,
    windows_up_to,
)
from app.infrastructure.adapters.cloudwatch import CloudWatchRdsAdapter, FallbackRdsAdapter
from app.infrastructure.adapters.flagship_reader import FlagshipMetricsAdapter
from app.infrastructure.adapters.grafana import GrafanaClient
from app.infrastructure.adapters.output import ConsoleAndFileOutputAdapter
from app.infrastructure.adapters.resilience import describe_error
from app.infrastructure.adapters.revolut_reader import RevolutMetricsAdapter
from app.infrastructure.logging import (
    REPORT_GENERATION_COMPLETED,
    REPORT_GENERATION_FAILED,
    REPORT_GENERATION_STARTED,
    configure_logging,
    log_event,
)
from app.infrastructure.settings import load_settings


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Gera relatorio diario de observabilidade (Flagship DTW ou Revolut MIP)."
    )
    parser.add_argument(
        "--client",
        choices=["flagship", "revolut"],
        default="flagship",
    )
    parser.add_argument("--date", default=None)
    parser.add_argument("--window", choices=WINDOW_ORDER, default=None)
    parser.add_argument("--chamados-hml", default="Sem ocorrências.")
    parser.add_argument("--chamados-prd", default="Sem ocorrências.")
    parser.add_argument("--chamados", default="Sem ocorrências.")
    parser.add_argument("--responsavel", default="Victor Silveira")
    parser.add_argument("--output", "-o", default=None)
    parser.add_argument("--skip-rds", action="store_true")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    logger = configure_logging()
    try:
        return _run_cli(args, logger)
    except Exception as exc:
        reason = describe_error(exc)
        log_event(
            logger,
            logging.ERROR,
            REPORT_GENERATION_FAILED,
            client=args.client,
            reason=reason,
        )
        print(
            f"Erro: Não foi possível gerar relatório no cliente {args.client} por {reason}.",
            file=sys.stderr,
        )
        return 1


def _run_cli(args: argparse.Namespace, logger: logging.Logger) -> int:
    settings = load_settings()

    target_date = date.fromisoformat(args.date) if args.date else datetime.now(BRT).date()
    window_key = args.window or detect_current_window()
    current_window = build_time_window(target_date, window_key)
    day_windows = windows_up_to(target_date, window_key)

    log_event(
        logger,
        logging.INFO,
        REPORT_GENERATION_STARTED,
        client=args.client,
        date=current_window.date_label,
        window=current_window.key,
    )

    output_port = ConsoleAndFileOutputAdapter(Path(args.output) if args.output else None)

    if args.client == "revolut":
        revolut_reader = RevolutMetricsAdapter(settings)
        revolut_uc = GenerateRevolutReportUseCase(revolut_reader, output_port)
        revolut_uc.execute(
            GenerateRevolutReportCommand(
                current_window=current_window,
                day_windows=day_windows,
                responsavel=args.responsavel,
                chamados=args.chamados,
            )
        )
    else:
        flagship_reader = FlagshipMetricsAdapter(settings)
        rds_reader = FallbackRdsAdapter(
            CloudWatchRdsAdapter(settings.cloudwatch_rds_url),
            GrafanaClient(
                base_url=settings.grafana_prd_base,
                username=settings.grafana_user,
                password=settings.grafana_pass,
            ),
        )
        flagship_uc = GenerateFlagshipReportUseCase(flagship_reader, rds_reader, output_port)
        flagship_uc.execute(
            GenerateFlagshipReportCommand(
                current_window=current_window,
                day_windows=day_windows,
                chamados_hml=args.chamados_hml,
                chamados_prd=args.chamados_prd,
                skip_rds=args.skip_rds,
            )
        )

    log_event(
        logger,
        logging.INFO,
        REPORT_GENERATION_COMPLETED,
        client=args.client,
        window=current_window.key,
        output=args.output or "stdout",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
