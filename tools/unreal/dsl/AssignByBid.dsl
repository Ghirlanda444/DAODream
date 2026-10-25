(fn AssignByBid (Follower)
  (Variabili|Predefinito|ImpostaBestDist 1200.0)
  (Variabili|Predefinito|ImpostaBestTarget)
  (bind _all (Attore|GetAllActorsOfClass "/Game/Cousland/Dialogue/BP_DlgNPC.BP_DlgNPC_C"))
  (for _a _all
    (Classe|BPDlgNPC|Bid _a :InMgr (Variabili|Ottieniunriferimentoasestesso) :From Follower))
  (Classe|BPDlgNPC|SetTarget Follower :InTarget (Variabili|Predefinito|OttieniBestTarget)))
