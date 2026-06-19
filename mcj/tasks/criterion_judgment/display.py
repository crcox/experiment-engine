from mcj.runtime.profiles import FeedbackStimulusConfig, ResponseMarkConfig
from mcj.runtime.display_primitives import StimFactory

TASK="criterion_judgment"

class CriterionJudgmentPromptDisplay:
    def __init__(self, factory: StimFactory):
        self.prompt_frame = factory.create_text(
            name=f"{TASK}_prompt_frame",
            pos=(0, .2),
            height=.05,
            wrap_width=.6,
            color='white',
        )
        self.prompt = factory.create_text(
            name=f"{TASK}_prompt",
            pos=(.0, .0),
            height=.05,
            color='white',
        )
        self.left_label = factory.create_text(
            name=f"{TASK}_left_label",
            pos=(-.3, -.3),
            height=0.04,
            color="lightgrey",
        )
        self.right_label = factory.create_text(
            name=f"{TASK}_right_label",
            pos=(.3, -.3),
            height=0.04,
            color="lightgrey",
        )

    def update(
        self,
        *,
        prompt_frame_text: str,
        prompt_text: str,
        left_text: str,
        right_text: str,
    ):
        self.prompt_frame.set_text(prompt_frame_text)
        self.prompt.set_text(prompt_text)
        self.left_label.set_text(left_text)
        self.right_label.set_text(right_text)

    def draw(self):
        self.prompt_frame.draw()
        self.prompt.draw()
        self.left_label.draw()
        self.right_label.draw()


class CriterionJudgmentDefinitionDisplay:
    def __init__(self, factory: StimFactory):
        self.definition = factory.create_text(
            name=f"{TASK}_definition",
            pos=(0., .0),
            height=.05,
            wrap_width=.6,
            color='white',
        )
        self.left_label = factory.create_text(
            name=f"{TASK}_left_label",
            pos=(-.3, -.3),
            height=0.04,
            color="lightgrey",
        )
        self.right_label = factory.create_text(
            name=f"{TASK}_right_label",
            pos=(.3, -.3),
            height=0.04,
            color="lightgrey",
        )

    def update(
        self,
        *,
        definition_text: str,
        left_text: str,
        right_text: str,
    ):
        self.definition.set_text(definition_text)
        self.left_label.set_text(left_text)
        self.right_label.set_text(right_text)

    def draw(self):
        self.definition.draw()
        self.left_label.draw()
        self.right_label.draw()


class CriterionJudgmentStimulusDisplay:
    def __init__(self, factory: StimFactory, response_mark_cfg: ResponseMarkConfig | None):

        self.cue = factory.create_text(
            name=f"{TASK}_cue",
            pos=(.0, .0),
            height=0.04,
            color="white",
        )
        self.prompt = factory.create_text(
            name=f"{TASK}_prompt",
            pos=(.0, .3),
            height=0.04,
            color="lightgrey",
        )
        self.left_label = factory.create_text(
            name=f"{TASK}_left_label",
            pos=(-.3, -.3),
            height=0.04,
            color="lightgrey",
        )
        self.right_label = factory.create_text(
            name=f"{TASK}_right_label",
            pos=(.3, -.3),
            height=0.04,
            color="lightgrey",
        )
        if response_mark_cfg:
            self.response_mark = factory.create_text(
                name=f"{TASK}_response_mark",
                pos=(0, response_mark_cfg.y_offset),
                height=response_mark_cfg.height,
                color=response_mark_cfg.color,
            )
        else:
            self.response_mark = factory.create_text(
                name=f"{TASK}_response_mark",
                pos=(0,-.1),
                height=0.03,
                color="lightgrey",
            )

    def update(
        self,
        *,
        cue_text: str,
        prompt_text: str,
        left_text: str,
        right_text: str,
    ):
        self.cue.set_text(cue_text)
        self.prompt.set_text(prompt_text)
        self.left_label.set_text(left_text)
        self.right_label.set_text(right_text)

    def draw(self):
        self.prompt.draw()
        self.cue.draw()
        self.left_label.draw()
        self.right_label.draw()
        if self.is_marked:
            self.response_mark.draw()

    def mark_response(self, response: str):
        self.response_mark.set_text(response)

    @property
    def is_marked(self):
        return self.response_mark.get_text() != ""

    def clear_response_mark(self) -> None:
        self.response_mark.set_text("")

class CriterionJudgmentFeedbackDisplay:
    def __init__(self, factory: StimFactory):
        self.feedback = factory.create_text(
            name=f"{TASK}_feedback",
            pos=(.0, .0),
            height=0.04,
            color="black",
        )

    def update(self, config: FeedbackStimulusConfig):
        self.feedback.set_text(config.text)
        self.feedback.set_color(config.color)

    def draw(self):
        self.feedback.draw()
