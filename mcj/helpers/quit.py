from mcj.adapters.psychopy.protocols import WindowLike

def quit_psychopy(win: WindowLike | None) -> None:
    if win is not None:
        win.clearAutoDraw()
        win.flip()
        win.close()

