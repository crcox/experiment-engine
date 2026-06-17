- 2026-06-10 17:35:33 — while working in c:\Users\chriscox\OneDrive - Louisiana State University\Research\MRI\Faith Coleman Semantic Warping\LSU Experiment Files\MCJ\mcj\xid\interface.py
 It seems that XidInterface is not being referenced anywhere... maybe it's safe to remove. 

- 2026-06-10 17:40:24 — while working in c:\Users\chriscox\OneDrive - Louisiana State University\Research\MRI\Faith Coleman Semantic Warping\LSU Experiment Files\MCJ\mcj\xid\real.py
 Not sure what is going on with this ftd2xx import... I don't remember why this is wired up like this. 

- 2026-06-11 05:36:02 — while working in c:\Users\chriscox\OneDrive - Louisiana State University\Research\MRI\Faith Coleman Semantic Warping\LSU Experiment Files\MCJ\mcj\runtime\sceens.py
 ScreenConfig does not seem to be referenced anywhere in the project.

- 2026-06-12 14:21:49 — while working in C:\Users\chriscox\OneDrive - Louisiana State University\Research\MRI\Faith Coleman Semantic Warping\LSU Experiment Files\MCJ\mcj\components\feedback.py
 The generic feedback component may not be being used. 

- 2026-06-12 14:24:23 — while working in C:\Users\chriscox\OneDrive - Louisiana State University\Research\MRI\Faith Coleman Semantic Warping\LSU Experiment Files\MCJ\mcj\runtime\time.py
 This Timer class feels obsolete. 

- 2026-06-12 14:26:16 — while working in C:\Users\chriscox\OneDrive - Louisiana State University\Research\MRI\Faith Coleman Semantic Warping\LSU Experiment Files\MCJ\mcj\components\question_text.py
 This QuestionText feels obsolete 

- 2026-06-15 10:19:50 — while working in C:\Users\chriscox\OneDrive - Louisiana State University\Research\MRI\Faith Coleman Semantic Warping\LSU Experiment Files\MCJ\mcj\runtime\setup.py
 The final point is that we have written functions recently that take their
 context from SessionInfo, rather than from SessionContext. I want to ensure
 that the concepts of SessionContext and SessionInfo are cleanly distinct, or
 they are collapsed into one.

 Previously, SessionInfo captured configuration choices made by the
 experimenter at runtime. In other words, its original purpose was to collect
 information from the UI Dialog that popped up before the session began. Now,
 we can get SessionInfo potentially from dev script, potentially from
 environment variables, potentially from command line arguments, and
 potentially from that UI Dialog, depending on how the code is being run. I
 think SessionInfo still serves a critical function as that configuration
 interface. But I also think we should ingest SessionInfo into a strictly typed
 SessionContext before we start to realize the influence of those configuration
 requests. SessionContext also holds things like TaskPlans, the authoratiative
 reference to the clock, the InputManager, and the EventRecorder.

 I was going to say that we should be passing SessionContext into the input
 adapter factories, not SessionInfo... but now that I have written this out,
 it's clear that we need to define the InputAdapterFactories before we can
 resolve the input adapter, and we need to resolve the input adapter before we
 build SessionContext. So the flow makes sense as it is currently written...
 this is just one of the many places that the code is going to need to be
 clearly documented so that people understand that abstractions and the flow of
 control and data/configuration. 

- 2026-06-15 12:02:39 — while working in C:\Users\chriscox\OneDrive - Louisiana State University\Research\MRI\Faith Coleman Semantic Warping\LSU Experiment Files\MCJ\mcj\runtime\input_config.py
 SessionInfo: configuration input (UI, CLI, env)
SessionContext: realized runtime system

Flow:
    SessionInfo
        ↓
    build_session()
        ↓
    resolve_input_adapters()
        ↓
    construct SessionContext 

- 2026-06-15 12:05:51 — while working in C:\Users\chriscox\AppData\Local\nvim\lua\config\notes.lua
 Just checking that the whitespace problem is fixed! :) It is. 
