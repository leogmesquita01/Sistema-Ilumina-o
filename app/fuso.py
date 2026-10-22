"""Utilitários de fuso horário.

O servidor (ex.: Streamlit Cloud) roda em UTC, e o banco grava datas em UTC.
Tudo o que é exibido ao usuário deve ser convertido para o horário local de
Boa Saúde / RN (America/Fortaleza, UTC-3, sem horário de verão).
"""
import datetime

try:
    from zoneinfo import ZoneInfo

    FUSO_LOCAL = ZoneInfo("America/Fortaleza")
except Exception:  # sem base tzdata disponível: Brasil não tem horário de verão desde 2019
    FUSO_LOCAL = datetime.timezone(datetime.timedelta(hours=-3), "BRT")


def agora_local() -> datetime.datetime:
    """Data/hora atual no fuso de Boa Saúde / RN, independente do fuso do servidor."""
    return datetime.datetime.now(FUSO_LOCAL)


def para_local(valor) -> datetime.datetime | None:
    """Converte um timestamp do banco (UTC) para o fuso local.

    Aceita `datetime` ou texto nos formatos do SQLite (`YYYY-MM-DD HH:MM:SS`)
    e ISO 8601 do Supabase (`...+00:00` / `...Z`). Valores sem fuso são
    tratados como UTC. Retorna None se não for possível interpretar.
    """
    if not valor:
        return None
    if isinstance(valor, datetime.datetime):
        dt = valor
    else:
        texto = str(valor).strip().replace("Z", "+00:00")
        try:
            dt = datetime.datetime.fromisoformat(texto)
        except ValueError:
            return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=datetime.timezone.utc)
    return dt.astimezone(FUSO_LOCAL)
