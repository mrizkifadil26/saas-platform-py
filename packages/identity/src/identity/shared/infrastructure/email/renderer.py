from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape

from identity.shared.infrastructure.email.message import EmailMessage

from .template import EmailTemplate


class EmailTemplateRenderer:
    def __init__(
        self,
        *,
        shared_template_dir: Path,
        feature_template_dirs: list[Path] | None = None,
    ) -> None:
        template_dirs = [
            *(feature_template_dirs or []),
            shared_template_dir,
        ]

        self._environment = Environment(
            loader=FileSystemLoader(template_dirs),
            autoescape=select_autoescape(
                enabled_extensions=("html", "xml"),
                default_for_string=False,
            ),
            trim_blocks=True,
            lstrip_blocks=True,
        )

    def render(
        self,
        template: EmailTemplate,
    ) -> EmailMessage:
        context = template.context()

        subject = self._render(
            f"{template.name}/subject.j2",
            context,
        )

        text = self._render(
            f"{template.name}/text.j2",
            context,
        )

        html = self._render(
            f"{template.name}/html.j2",
            context,
        )

        return EmailMessage(
            recipient=template.recipient,
            subject=subject,
            text=text,
            html=html,
        )

    def _render(
        self,
        template_name: str,
        context: dict[str, object],
    ) -> str:
        template = self._environment.get_template(template_name)

        return template.render(**context)
