I am working on a PsychoPy-based experiment system with:

- Event-driven runtime (EventRecorder, emitters, JSON logging)
- InputManager coordinating multiple InputAdapters
- There is currently a KeyboardAdapter and a CedrusAdapter (Cedrus uses device clock in ms)
- Protocol-based typing boundaries (e.g., XidDeviceLike)
- TaskPlan is now Generic[TBlock]
- Logging system uses EventTypeLogger / SamplingLogger / PredicateLogger

Critical detail:
- This experiment will be administered to participants while being scanned with
  fMRI.
- The Cedrus collects response-pad button presses and scanner triggers on the
  same port. Response-pad buttons are associated with codes in [0, 3], and
  scanner triggers are associated with code=4.
- Cedrus alignment must map device ms timestamps -> system clock time
- Timing must be accurate at the point of device ingestion
- InputManager.update() consumes device events
- I recently moved from blocking `await_alignment()` -> non-blocking loop

Current problem:
I am working on how to align the clocks held by the Cedrus device and my
system. There are two options I am considering for achieving this:

Option 1:
My first attempt involved waiting for a scanner trigger. The ideas was
to compare the timestamp for the trigger event provided by the Cedrus device to
system times immediately preceeding and following that event. However, this is
complicated by the fact that we don't know when the trigger will be initiated.
We must await to detect an event, which will occur in a loop and have some
degree of error associated with it, especially because we will need to align
the device clock with the earliest measured system time after receiving the
signal, despite the fact that the trigger might have arrived at any point since
the last iteration of the loop. Despite this innaccurary, if the loop is fast
enough, it the error will be small.

The procedure would be something like:

- Loop with some small time.sleep() increment to keep from pegging CPU at 100%
- Monitor Input Manager for inputs, which owns and manages interactions with
  the Cedrus Input Adapter.
- If one is detected, immediately note the time as our potential `t0_system`.
- Check if the input is a scanner trigger.
- If it is, set `t0_device = event.time`, where `event.time` is the timestamp
  from the Cedrus device's Reaction Time Timer (see below).
- Store these two values on the Cedrus Input Adapter instance.
- When receiving event timestamps in the future, we do:
    `evt["time"] - t0_device + t0_system`

Option 1:
There is a possible alternative worth exploring that could be more accurate.
The Cedrus can also receive a limited number of commands relevant to timing.

To quote the documentation for the XIDv1 protocol provided by Cedrus:

<quote>

|---------------------------+------------+------------------------------------------|
| Command                   | Send Bytes | What Happens:                            |
|---------------------------+------------+------------------------------------------|
| Reset Base Timer          | e1         | The base timer is reset to zero          |
|---------------------------+------------+------------------------------------------|
| Query Elapsed Time        | e3         | The XID device sends back e3 followed by |
|                           |            | four bytes indicating the number of      |
|                           |            | milliseconds that have elapsed since the |
|                           |            | BaseTimer was reset.                     |
|---------------------------+------------+------------------------------------------|
| Reset Reaction Time Timer | e5         | The Reaction Time Timer is set to zero   |
|---------------------------+------------+------------------------------------------|

The Base Timer is always running. Typically, this timer is reset at the start
of an experiment or session, and can later be queried at any time to determine
how much time has elapsed.

The Reaction Time Timer is also always running but works differently from the
Base Timer. Typically, this timer is reset at the onset of a trial. The
application then continues to do more work or simply waits for the XID device
to respond. When the XID device detects input from the participant, it sends
that information to the host computer time stamped with the participant's
reaction time.

</quote>

However, I do not want to reset clocks throughout the experiment. My aim is to
have a continuous event log, and reconstruct response times after the fact.

Therefore, it is unfortunate that we can manually query only the Base Timer,
but are reliant on events that we do not initiate to receive timestamps from
the Reaction Time Timer.

However, practically speaking, it will probably be good enough to:

send e1 (reset base clock)
send e5 (reset rt clock)
send e3 (query base clock)

I presume that the latency between e1 and e 3 will be low, and that we can
effectively use the time returned for the baseclock as identical to the time on
the rt clock.

Because we will initiate these commands outselves, we will know the system time
immediately before sending the first command and the system time immediately
following the final command.

Given that Option 2 would be considerably more effort and would rely on
physical access to the system, which I do not have except during limited
scheduled windows, I would like to avoid it if possible. However, I will not
shy away from doing what is needed to achieve accurate timing.

I would appreciate your help with the following:
1. Do you think Option 1 will be reasonably accurate?
2. Can you give me a stepwise workflow for implementing it carefully?
3. If Option 2 is necessary, I will have many more questions for you.
