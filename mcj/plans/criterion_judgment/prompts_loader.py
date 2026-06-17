from pathlib import Path
from functools import lru_cache
from dataclasses import dataclass
import yaml
from typing import Mapping
from mcj.runtime.exceptions import DataContractError
from mcj.plans.criterion_judgment.schema import (
    CriterionJudgmentCondition as Condition
)

@dataclass(frozen=True)
class PromptConfig:
    prompt_frame: str
    prompt: str
    definition: str | None = None

    @property
    def has_definition(self) -> bool:
        return self.definition is not None

    def require_definition(self) -> str:
        if self.definition is None:
            raise RuntimeError("This operation requires a definition to be specified.")
        return self.definition


@lru_cache
def _load_prompts() -> Mapping[Condition, PromptConfig]:
    here = Path(__file__).parent
    yaml_path = here / "prompts.yaml"

    with open(yaml_path, 'r') as f:
        data = yaml.safe_load(f)

    if "conditions" not in data or not isinstance(data["conditions"], dict):
        raise DataContractError("Prompts file must contain a list of conditions")

    prompts = {}
    required_fields = {"prompt_frame", "prompt"}
    optional_fields = {"definition"}
    for condition, config in data["conditions"].items():
        missing = required_fields - set(config.keys())
        if missing:
            raise DataContractError(f"Condition {condition!r} is missing required fields: {missing!r}. Check {yaml_path}.")
        for field in required_fields:
            if not isinstance(config[field], str):
                raise DataContractError(f"Config {field!r} must be a string. Check {yaml_path}.")

        for field in optional_fields:
            if field in config and not isinstance(config[field], str):
                raise DataContractError(f"Config {field!r} must be a string. Check {yaml_path}.")

        prompts[Condition(condition)] = PromptConfig(
            prompt_frame=config['prompt_frame'],
            prompt=config['prompt'],
            definition=config.get('definition', None)
        )

    return prompts


def load_prompt(condition: Condition) -> PromptConfig:
    prompts = _load_prompts()
    return prompts[condition]

