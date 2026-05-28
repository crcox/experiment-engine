from psychopy.visual.window import Window
from psychopy.visual.text import TextStim
from dataclasses import dataclass, replace
from mcj.runtime.exceptions import DataContractError
from typing import TypeAlias

WORDS = ["bear", "crocodile", "rhinocerous", "shark", "tiger", "wolf", "lamb",
         "sheep", "dolphin", "peacock", "llama", "pony", "infectious mosquito",
         "scorpion", "black widow", "hornet", "rattlesnake", "piranha",
         "butterfly", "ladybug", "bunny", "frog", "goldfish", "gecko",
         "wrecking ball", "cannon", "power line", "torpedo", "wood chipper",
         "missle", "mattress", "guitar", "couch", "desk", "piano",
         "refrigerator", "handgun", "knife", "dagger", "razor", "grenade",
         "hammer", "glove", "whisk", "brush", "phone", "sponge", "spoon"]

@dataclass(frozen=True)
class Word:
    word: str
    domain: str
    size: str
    danger: str
    orthography: str
    stimulus: TextStim | None

    def __post_init__(self):
        if not self.domain in ["living", "nonliving"]:
            raise DataContractError()

        if not self.size in ["big", "small"]:
            raise DataContractError()

        if not self.danger in ["safe", "dangerous"]:
            raise DataContractError()

        if not self.orthography in ["uppercase", "lowercase"]:
            raise DataContractError()

    @property
    def is_living(self) -> bool:
        return self.domain == "living"

    @property
    def is_big(self) -> bool:
        return self.size == "big"

    @property
    def is_safe(self) -> bool:
        return self.danger == "safe"

    @property
    def is_uppercase(self) -> bool:
        return self.orthography == "uppercase"

    def build_stimulus(self, win: Window) -> TextStim:
        return TextStim(
            win,
            text=self.word,
            name=f"word_{self.word}",
            color=[1.0, 1.0, 1.0],
            colorSpace="rgb"
        )

    def add_stimulus(self, win: Window) -> Word:
        return replace(self, stimulus=self.build_stimulus(win))


StimulusPool: TypeAlias = dict[Word, TextStim]

