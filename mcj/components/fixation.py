from psychopy.visual.window import Window
from mcj.components.typed_stim import TypedShapeStim

class FixationCross(TypedShapeStim):
    def __init__(self, win: Window, **kwargs):
        super().__init__(
            win=win,
            name='fixation_cross',
            vertices='cross',
            size=(0.1, 0.1),
            pos=(0, 0),
            draggable=False,
            anchor='center',
            lineWidth=0.05,
            colorSpace='rgb',
            lineColor='white',
            fillColor='black',
            interpolate=True,
            **kwargs
        )
    
