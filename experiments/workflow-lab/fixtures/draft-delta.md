DRAFT DELTA after answer A.1

CHANGED
  [replace][G.2][UNKNOWN -> DECISION][owner=user] Multiple independent users must sign in.
  [replace][T.1][ASSUMPTION -> ASSUMPTION][owner=agent][risk=high][falsifier=identity-provider spike cannot isolate users][x-trigger=X.2] Use the existing identity provider for the first vertical slice.
  [remove][X.1][UNKNOWN] Intended audience is now resolved.
  [add][X.2][UNKNOWN][blocking=true][deferred=false] Stop if the existing identity provider cannot isolate user data.

READINESS CHANGED
  ready: no -> no
  blocking: X.1 -> X.2
  next-question-reason: the persistence answer changes the data-isolation boundary

UNCHANGED
  omitted by contract
