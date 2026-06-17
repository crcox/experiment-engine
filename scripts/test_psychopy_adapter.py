from tests.fakes.display import FakeFactory
from mcj.tasks.criterion_judgment.display import CriterionJudgmentPromptDisplay

display = CriterionJudgmentPromptDisplay(FakeFactory())

display.update(
    prompt_frame_text="Frame",
    prompt_text="Hello",
    left_text="Left",
    right_text="Right",
)

display.draw()
