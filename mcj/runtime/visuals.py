from dataclasses import dataclass
from psychopy.visual.rect import Rect

@dataclass
class SequenceMTSVisuals:
    highlight: Rect

@dataclass
class FamiliarizationVisuals:
    highlight: Rect
