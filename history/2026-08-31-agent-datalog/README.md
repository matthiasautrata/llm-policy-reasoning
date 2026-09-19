# Agent-written Datalog, 31 August 2026

In the mandatory-oracle runs of Study 1 (prompt p18), no query engine was actually attached. The agent (DeepSeek V4 Pro in Hermes) translated the prompt's Datalog into Soufflé syntax itself and ran it. These are the files it left in the working folder: `proc/` (several program variants and their outputs) and `procurement_oracle/`.

All four program variants produce identical relations, and they agree with `study1-interpretation/oracle/large/`. The transcripts of these runs are in `study1-interpretation/transcripts/`.
