import os
from pathlib import Path
from typing import Optional

from chainlit.logger import logger

from ._utils import is_path_inside

# Default chainlit.md file created if none exists
DEFAULT_MARKDOWN_STR = """# Welcome to ArchiCode Guide!

Hello, Architects, Engineers and Builders! 👋 

ArchiCode Guide is your AI-powered assistant for navigating the very complex Indian National Building Code and architectural regulations. Ask any question about NBC 2016 (currently only for the fire and life safety chapter) requirements, and get instant, accurate answers with citations.

## How to use ArchiCode Guide

- Ask specific questions about building code requirements
- Get answers with direct citations to code sections
- Explore related regulations through follow-up questions

## Example questions

- "What are the requirements for fire separations in residential buildings?"
- "Explain the exit requirements for a 3-story office building"
- "Show me the fire resistance ratings for load-bearing walls"

Built with ❤️ for AEC professionals everywhere

---


*P.S. Currently, ArchiCode Guide only contains data from the Fire and Life Safety chapter of NBC 2016. Support for additional chapters is coming soon!*
"""


def init_markdown(root: str):
    """Initialize the chainlit.md file if it doesn't exist."""
    chainlit_md_file = os.path.join(root, "chainlit.md")

    if not os.path.exists(chainlit_md_file):
        with open(chainlit_md_file, "w", encoding="utf-8") as f:
            f.write(DEFAULT_MARKDOWN_STR)
            logger.info(f"Created default chainlit markdown file at {chainlit_md_file}")


def get_markdown_str(root: str, language: str) -> Optional[str]:
    """Get the chainlit.md file as a string."""
    root_path = Path(root)
    translated_chainlit_md_path = root_path / f"chainlit_{language}.md"
    default_chainlit_md_path = root_path / "chainlit.md"

    if (
        is_path_inside(translated_chainlit_md_path, root_path)
        and translated_chainlit_md_path.is_file()
    ):
        chainlit_md_path = translated_chainlit_md_path
    else:
        chainlit_md_path = default_chainlit_md_path
        logger.warning(
            f"Translated markdown file for {language} not found. Defaulting to chainlit.md."
        )

    if chainlit_md_path.is_file():
        return chainlit_md_path.read_text(encoding="utf-8")
    else:
        return None
