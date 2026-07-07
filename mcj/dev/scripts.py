from mcj.runtime.scripting.builder import ScriptBuilder
from mcj.runtime.scripting.primitives import respond_left, fixation, feedback, respond_left_cedrus, instruction_slide, sequence

def test_dev_script():
    trial = sequence(fixation, respond_left, feedback)

    return (
        ScriptBuilder()
        .press("space")  # instruction [slide 1]
        .press("space")  # instruction [slide 2]
        .press("space")  # prompt [size]
        .press("space")  # definition [size]
        .repeat(48, trial)
        .press("space")  # prompt [domain]
        .repeat(48, trial)
        .press("space")  # prompt [danger]
        .press("space")  # definition [size]
        .repeat(48, trial)
        .press("space")  # prompt [orthography]
        .repeat(48, trial)
        .press("space")  # prompt [danger]
        .press("space")  # definition [danger]
        .repeat(48, trial)
        .press("space")  # prompt [size]
        .press("space")  # definition [size]
        .repeat(48, trial)
        .press("space")  # prompt [orthography]
        .repeat(48, trial)
        .press("space")  # prompt [domain]
        .repeat(48, trial)
        .build()
    )

def test_dev_scanner_script():
    trial = sequence(fixation, respond_left_cedrus, feedback)

    def block_with_definition(s: ScriptBuilder):
        return (
            s.trigger(target="cedrus")
             .press("space", target="keyboard")
             .press("space", target="keyboard")
             .repeat(48, trial)
        )

    def block_without_definition(s: ScriptBuilder):
        return (
            s.trigger(target="cedrus")
             .press("space", target="keyboard")
             .repeat(48, trial)
        )

    danger_block      = block_with_definition
    domain_block      = block_without_definition
    orthography_block = block_without_definition
    size_block        = block_with_definition

    return (
        ScriptBuilder()
        .repeat(2, instruction_slide)
        .repeat(1, size_block)
        .repeat(1, domain_block)
        .repeat(1, danger_block)
        .repeat(1, orthography_block)
        .repeat(1, danger_block)
        .repeat(1, size_block)
        .repeat(1, orthography_block)
        .repeat(1, domain_block)
        .build()
    )

def test_scanner_script():
    trial = sequence(fixation, respond_left_cedrus)

    return (
        ScriptBuilder()
        .press("space")  # instruction [slide 1]
        .press("space")  # instruction [slide 2]
        .press("space")  # prompt [size]
        .repeat(48, trial)
        .build()
    )
