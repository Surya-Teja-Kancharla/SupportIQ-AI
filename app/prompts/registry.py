from dataclasses import dataclass
from typing import Callable

from app.prompts.ticket_analysis_v1 import (
    PROMPT_NAME,
    PROMPT_VERSION,
    SYSTEM_PROMPT,
    build_user_prompt,
)


@dataclass(frozen=True)
class PromptDefinition:
    name: str
    version: str
    system_prompt: str
    user_prompt_builder: Callable[..., str]


PROMPT_REGISTRY = {
    PROMPT_VERSION: PromptDefinition(
        name=PROMPT_NAME,
        version=PROMPT_VERSION,
        system_prompt=SYSTEM_PROMPT,
        user_prompt_builder=build_user_prompt,
    ),
}


def get_prompt(version: str) -> PromptDefinition:
    try:
        return PROMPT_REGISTRY[version]
    except KeyError as exc:
        raise ValueError(
            f"Unsupported prompt version: {version}"
        ) from exc
