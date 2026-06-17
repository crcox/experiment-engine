from mcj.runtime.display_primitives import StimFactory

class FixationDisplay:
    def __init__(self, factory: StimFactory):
        self.fixation_cross = factory.create_known_shape(
            name='fixation_cross',
            shape='cross',
            size=(0.03, 0.03),
            pos=(0, 0),
            color='white'
        )

    def update(
        self,
    ):
        pass

    def draw(self):
        self.fixation_cross.draw()
