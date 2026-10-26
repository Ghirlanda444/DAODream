(fn FindTarget ()
  (Variabili|Predefinito|ImpostaBestDist 230.0)
  (Variabili|Predefinito|ImpostaBestTarget)
  (bind _all (Attore|GetAllActorsOfClass "/Game/Cousland/Dialogue/BP_DlgNPC.BP_DlgNPC_C"))
  (for _a _all
    (Funzionedichiamata|TalentBid :Npc _a))
  (Funzionedichiamata|PreferTarget :Reach 230.0))
