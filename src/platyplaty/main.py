#!/usr/bin/env python3
"""Main entry point for the Platyplaty visualizer client.

This module provides the CLI interface using click. Only click is imported
at module level to ensure fast --help response times.
"""

import click


@click.command()
@click.option(
    "--config-file",
    type=click.Path(exists=True),
    help="Path to TOML configuration file.",
)
@click.option(
    "--generate-config",
    type=str,
    metavar="PATH",
    help="Generate example config to PATH (use '-' for stdout).",
)
@click.option(
    "--playlist",
    type=click.Path(),
    help="Path to .platy playlist file to load at startup.",
)
def main(
    config_file: str | None,
    generate_config: str | None,
    playlist: str | None,
) -> None:
    """Platyplaty - A music visualizer using projectM."""
    # Mutual exclusivity check
    if config_file and generate_config:
        raise click.UsageError(
            "--config-file and --generate-config are mutually exclusive."
        )

    # Handle --generate-config
    if generate_config is not None:
        from platyplaty.generate_config import generate_config as gen_config

        try:
            gen_config(generate_config)
        except FileExistsError as e:
            raise click.ClickException(str(e)) from None
        return

    # Handle --config-file
    if config_file is not None:
        import sys

        from platyplaty.startup import run_with_config
        sys.exit(run_with_config(config_file, playlist))

    # No arguments: show error with suggestion
    raise click.UsageError(
        "No arguments provided. Use --generate-config to create a config file."
    )
