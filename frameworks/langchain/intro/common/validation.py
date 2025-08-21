from typing import List, Tuple
from rich.table import Table
from .models import Suggestion

MAX_VISIBLE_LENGTH = 70


def _get_visible_length(text: str) -> int:
    """Cuenta solo caracteres visibles, excluyendo caracteres de control y formato Unicode."""
    import unicodedata

    visible_chars = 0
    for char in text:
        if unicodedata.category(char) not in ("Cf", "Cc", "Mn"):
            visible_chars += 1
    return visible_chars

def build_validation_table(suggestions: List[Suggestion]) -> Tuple[Table, List[Suggestion]]:
    """Construye una tabla Rich con validación: coincide longitud reportada y visible, y visible < 70."""
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("#", justify="right", style="cyan", no_wrap=True)
    table.add_column("Título", style="white")
    table.add_column("Len visible", justify="right")
    table.add_column("Len reportada", justify="right")
    table.add_column("<70", justify="center")
    table.add_column("OK", justify="center")

    mismatches: List[Suggestion] = []

    for idx, s in enumerate(suggestions, start=1):
        visible_len = _get_visible_length(s.title)
        matches_reported = visible_len == s.length
        within_limit = visible_len < MAX_VISIBLE_LENGTH  # regla solicitada: menor que 70

        ok_all = matches_reported and within_limit
        if not ok_all:
            mismatches.append(s)

        limit_text = "[green]✔[/green]" if within_limit else "[red]✘[/red]"
        ok_text = "[green]✔[/green]" if ok_all else "[red]✘[/red]"

        table.add_row(
            str(idx), s.title, str(visible_len), str(s.length), limit_text, ok_text
        )

    return table, mismatches
