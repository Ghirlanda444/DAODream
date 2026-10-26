(fn HeroBid ()
  (Variabili|Predefinito|ImpostaHeroTarget)
  (Variabili|Predefinito|ImpostaBestDist 1200.0)
  (Variabili|Predefinito|ImpostaBestTarget)
  (bind _all (Attore|GetAllActorsOfClass "/Game/Cousland/Dialogue/BP_DlgNPC.BP_DlgNPC_C"))
  (for _a _all
    (Classe|BPDlgNPC|OrderOffer _a :InMgr (Variabili|Ottieniunriferimentoasestesso) :From (Gioco|GetPlayerPawn 0)))
  (Variabili|Predefinito|ImpostaHeroTarget (Utilità|Casting|CastToBP_DlgNPC (Variabili|Predefinito|OttieniBestTarget))))
