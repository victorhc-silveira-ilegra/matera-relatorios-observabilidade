from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv


@dataclass(frozen=True)
class Settings:
    kibana_hml_user: str
    kibana_hml_pass: str
    kibana_prd_user: str
    kibana_prd_pass: str
    grafana_user: str
    grafana_pass: str
    opensearch_hml_base: str
    opensearch_prd_base: str
    grafana_hml_base: str
    grafana_prd_base: str
    cloudwatch_rds_url: str
    grafana_revolut_user: str = ""
    grafana_revolut_pass: str = ""
    grafana_revolut_base: str = "https://grafana-pvtlink.mip.prd.revolut.maas.link"
    revolut_http_proxy: str = "http://10.150.8.18:3128"


def _require_env(name: str, default: str | None = None) -> str:
    val = os.getenv(name, default)
    if not val:
        raise ValueError(f"Variavel de ambiente obrigatoria ausente: {name}")
    return val


def load_settings(env_path: str | None = None) -> Settings:
    load_dotenv(dotenv_path=env_path)
    return Settings(
        kibana_hml_user=_require_env("KIBANA_HML_USER"),
        kibana_hml_pass=_require_env("KIBANA_HML_PASS"),
        kibana_prd_user=_require_env("KIBANA_PRD_USER"),
        kibana_prd_pass=_require_env("KIBANA_PRD_PASS"),
        grafana_user=_require_env("GRAFANA_DEFAULT_USER"),
        grafana_pass=_require_env("GRAFANA_DEFAULT_PASS"),
        opensearch_hml_base=_require_env(
            "OPENSEARCH_HML_BASE",
            "https://vpc-dtw-hml-es-fdhj7etngcaluic7k2txvjy7oe.us-east-1.es.amazonaws.com",
        ).rstrip("/"),
        opensearch_prd_base=_require_env(
            "OPENSEARCH_PRD_BASE",
            "https://vpc-dtw-prod-es-lb6ckd2rys7fxixatwf2ijtmqe.sa-east-1.es.amazonaws.com",
        ).rstrip("/"),
        grafana_hml_base=_require_env(
            "GRAFANA_HML_BASE",
            "https://grafana-hml-dtw.flagship.maas.link",
        ).rstrip("/"),
        grafana_prd_base=_require_env(
            "GRAFANA_PRD_BASE",
            "https://grafana-prod-dtw.flagship.maas.link",
        ).rstrip("/"),
        cloudwatch_rds_url=_require_env(
            "CLOUDWATCH_RDS_URL",
            "https://cloudwatch.amazonaws.com/dashboard.html?dashboard=Flagship-BlackFriday&context=eyJSIjoidXMtZWFzdC0xIiwiRCI6ImN3LWRiLTM3NTU1NTk1NTAyNyIsIlUiOiJ1cy1lYXN0LTFfWVRhT0hhUjY5IiwiQyI6InU4cWZhdjMzMnFuaWFhY3MxdGtyNnI3MmciLCJJIjoidXMtZWFzdC0xOjFkZjk3ODQyLTI0ZDItNDQxMi1iYmU2LTJkYmI4NDYzZDQ2MiIsIk0iOiJQdWJsaWMifQ%3D%3D&start=PT3H&end=null&autoRefresh=60",
        ),
        grafana_revolut_user=os.getenv("GRAFANA_REVOLUT_USER", ""),
        grafana_revolut_pass=os.getenv("GRAFANA_REVOLUT_PASS", ""),
        grafana_revolut_base=os.getenv(
            "GRAFANA_REVOLUT_BASE",
            "https://grafana-pvtlink.mip.prd.revolut.maas.link",
        ).rstrip("/"),
        revolut_http_proxy=os.getenv("REVOLUT_HTTP_PROXY", "http://10.150.8.18:3128"),
    )
