"""
Módulo para la gestión y visualización de errores durante el ensamblado.
"""
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

class ErrorHandler:
    """Gestiona la recolección y el reporte de errores de ensamblado."""
    def __init__(self):
        self._error_count: int = 0
        self._console = Console()

    def reportar(self, num_linea: int, mensaje: str, linea_original: str = "") -> None:
        """
        Registra un error y lo muestra en la consola con un formato claro.
        """
        self._error_count += 1
        texto_error = Text(f"Error: {mensaje}", style="bold red")
        panel_contenido = texto_error
        
        if linea_original:
            panel_contenido.append(f"\n\nEn la línea: {linea_original.strip()}")

        panel = Panel(
            panel_contenido,
            title=f"Error en la línea {num_linea}",
            border_style="red"
        )
        self._console.print(panel)

    def tiene_errores(self) -> bool:
        """Devuelve True si se ha reportado al menos un error."""
        return self._error_count > 0

    def resumen_final(self) -> None:
        """Muestra un resumen del proceso de ensamblado."""
        if self.tiene_errores():
            self._console.print(
                f"\n[bold red]El ensamblaje falló con {self._error_count} error(s).[/bold red]"
            )
        else:
            self._console.print(
                "\n[bold green]¡Ensamblaje completado exitosamente![/bold green]"
            )