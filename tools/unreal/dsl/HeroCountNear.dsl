(fn HeroCountNear ()
  (Variabili|Predefinito|ImpostaHTCount 0)
  (bind _all (Attore|GetAllActorsOfClass "/Game/Cousland/Dialogue/BP_DlgNPC.BP_DlgNPC_C"))
  (for _a _all
    (Classe|BPDlgNPC|NearOffer _a :InMgr (Variabili|Ottieniunriferimentoasestesso))))
