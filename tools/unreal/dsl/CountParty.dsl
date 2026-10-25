(fn CountParty ()
  (Variabili|Predefinito|ImpostaPartySize 1)
  (bind _all (Attore|GetAllActorsOfClass "/Game/Cousland/Dialogue/BP_DlgNPC.BP_DlgNPC_C"))
  (for _a _all
    (Funzionedichiamata|CountMember :Npc _a)))
