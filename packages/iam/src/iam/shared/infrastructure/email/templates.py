from pathlib import Path

from jinja2 import Environment, FileSystemLoader


class TemplateRenderer:
    def __init__(
        self,
        template_dir: Path,
    ) -> None:
        self._environment = Environment(
            loader=FileSystemLoader(template_dir),
            autoescape=True,
            trim_blocks=True,
            lstrip_blocks=True,
        )

    def render(
        self,
        template: str,
        **context: object,
    ) -> str:
        return self._environment.get(template).render(**context)
