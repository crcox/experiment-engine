from psychopy.visual.text import TextStim
from psychopy.visual.window import Window

class FeedbackText:
    def __init__(self, win: Window):
        self._rt = TextStim(
            win=win,
            name='feedback_rt',
            text='',
            font='Arial',
            pos=(0.0, 0.2),
            height=0.05,
            wrapWidth=None,
            color=(-1.0, -1.0, -1.0),
            colorSpace='rgb',
            languageStyle='LTR'
        )
    
        self._acc = TextStim(
            win=win,
            name='feedback_acc',
            text='',
            font='Arial',
            pos=(0.0, -0.2),
            height=0.05,
            wrapWidth=None,
            color=(-1.0, -1.0, -1.0),
            colorSpace='rgb',
            languageStyle='LTR'
        )
    

    def set_feedback(self, rt: float, accuracy: float) -> None:
        self._rt.text = f"Mean RT: {rt*1000:.0f} ms"
        self._acc.text = f"Accuracy: {accuracy*100:.1f}%"


    def draw(self) -> None:
        self._rt.draw()
        self._acc.draw()
