from mcj.runtime.scripted import ScriptBuilder, respond_left, fixation, feedback, sequence


def test_practice_script():
    trial = sequence(fixation, respond_left, feedback)

    return (
        ScriptBuilder()
        .press("space")  # instruction [slide 1]
        .press("space")  # instruction [slide 2]
        .press("space")  # prompt [size]
        .press("space")  # definition [size]
        .repeat(48, trial)
        .build()
    )

def test_scanner_script():
    trial = sequence(fixation, respond_left)

    return (
        ScriptBuilder()
        .press("space")  # instruction [slide 1]
        .press("space")  # instruction [slide 2]
        .press("space")  # prompt [size]
        .repeat(48, trial)
        .build()
    )
