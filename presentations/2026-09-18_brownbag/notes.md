There are few things that get me as excited as when I am struck with the inspiration for new experiment. I imagine you all feel similarly. And those of use who have been doing this for a while are also familiar with the meticulous grind that is experiment design. That's the hard work, in a lot of ways: we need to literally operationalize theory and hypotheses into sequences and patterns of stimuli on a computer screen and how we want people to behave when they see them. After the weeks or months of agonizing over design with friends and colleagues and students, I finally resolve that the design is good enough and breath a sigh of relief because "the hard part is over now... right?". Now it's just the straight forward technical labor of laying out the experiment in EPrime or PsychoPy or whatever experiment builder tool according to the plan. We should be piloting by next week... right?

And then reality sets in...the builder doesn't exactly allow you to do what you want without a lot of creativity; there is some bug to squash in the implementation, but it takes several minutes every time you want to check if your latest revision fixes the problem; the way the builder records results in a way that actively thwarts analysis and obscures what's going on with multiple conflicting time stamps. Oh, and because your experiment will interface with some specialized aparatus, you can only really test that it's working if you are plugged into that aparatus. Faith and I can tell you some horror stories over beer sometime of what the development workflow for our fMRI experiment has been like.

After the struggle and triumph of the experiment design phase, I always assume that implementing the experiment is going to be easy. But there are so many places for things to go wrong:

 * Coordinating timing between multiple pieces of hardware that have their own clocks.
 * Catching and properly handling response signals--including properly ignoring them when they are irrelevant.
 * Systematically iterating on an experiment to implement new variants.
 * Identifying why an experiment stops working, and has intermittent crashes.

Last year, Stan, Alex, and Faith, as well as my honors thesis students at the time Meghan Garcelon and Marissa Goldthorp (who are both starting PhD programs this semester, at UIowa and UTennessee, respectively), did a huge amount of behavioral experimentation. And all year long, we were confronted with the reality of experiment implementation: it felt like a lot of the time we were fighting our tool of choice, Psychopy. We spent a lot of time feeling stuck or confused while trying to get an experiment running. By the end of spring, I had a number of specific frustrations:

 * Debugging and trouble shooting is much too slow, because every test requires a slow startup time and then stepping through the experiment manually to get to the trouble spot.
 * The core logic of the experiment is tightly coupled with device input and with rendering and displaying screens. Because everything is interconnected, it is difficult to develop in one environment and deploy in another.
 * Builders will introduce confusing redundancy, which prevent the experiment from having a single source of truth about the state of the system at any point during the runtime.

After sitting with these frustrations, and spending some time exploring possible solutions, some principles of "good" experiment implementation began to crystalize for me:

 1. There should be one clock, and it should never pause or be reset.
 2. There should be one record of events that is added to in real time, can never be subtracted from, and preserves the order in which they occured.
