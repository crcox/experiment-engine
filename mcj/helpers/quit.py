from psychopy import core
from psychopy.visual.window import Window

def quit_psychopy(win: Window) -> None:
    win.clearAutoDraw()
    win.flip()
    win.close()
    core.quit()

