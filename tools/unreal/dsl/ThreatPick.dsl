(fn ThreatPick ()
  (Funzionedichiamata|SeePlayer)
  (bind _all (Attore|GetAllActorsOfClass "/Game/Cousland/Dialogue/BP_DlgNPC.BP_DlgNPC_C"))
  (for _a _all
    (Funzionedichiamata|SeeMember :Npc _a))
  (Funzionedichiamata|Retarget)
  (Funzionedichiamata|DropDownFoe))
