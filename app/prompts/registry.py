from dataclasses import dataclass
from typing import Callable

from app.prompts.reply_suggestion_v1 import (
    PROMPT_NAME as REPLY_SUGGESTION_PROMPT_NAME,
    PROMPT_VERSION as REPLY_SUGGESTION_PROMPT_VERSION,
    SYSTEM_PROMPT as REPLY_SUGGESTION_SYSTEM_PROMPT,
    build_user_prompt as build_reply_suggestion_user_prompt,
)
from app.prompts.ticket_analysis_v1 import (
    PROMPT_NAME as TICKET_ANALYSIS_PROMPT_NAME,
    PROMPT_VERSION as TICKET_ANALYSIS_PROMPT_VERSION,
    SYSTEM_PROMPT as TICKET_ANALYSIS_SYSTEM_PROMPT,
    build_user_prompt as build_ticket_analysis_user_prompt,
)


@dataclass(frozen=True)
class PromptDefinition:
    name: str
    version: str
    system_prompt: str
    user_prompt_builder: Callable[..., str]


PROMPT_REGISTRY = {
    TICKET_ANALYSIS_PROMPT_VERSION: PromptDefinition(
        name=TICKET_ANALYSIS_PROMPT_NAME,
        version=TICKET_ANALYSIS_PROMPT_VERSION,
        system_prompt=TICKET_ANALYSIS_SYSTEM_PROMPT,
        user_prompt_builder=build_ticket_analysis_user_prompt,
    ),
    REPLY_SUGGESTION_PROMPT_VERSION: PromptDefinition(
        name=REPLY_SUGGESTION_PROMPT_NAME,
        version=REPLY_SUGGESTION_PROMPT_VERSION,
        system_prompt=REPLY_SUGGESTION_SYSTEM_PROMPT,
        user_prompt_builder=build_reply_suggestion_user_prompt,
    ),
}


def get_prompt(version: str) -> PromptDefinition:
    try:
        return PROMPT_REGISTRY[version]
    except KeyError as exc:
        raise ValueError(
            f"Unsupported prompt version: {version}"
        ) from exc
