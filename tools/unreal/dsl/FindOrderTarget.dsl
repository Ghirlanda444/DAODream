(fn FindOrderTarget ()
  (Variabili|Predefinito|ImpostaBestDist 1500.0)
  (Variabili|Predefinito|ImpostaBestTarget)
  (bind _all (Attore|GetAllActorsOfClass "/Game/Cousland/Dialogue/BP_DlgNPC.BP_DlgNPC_C"))
  (for _a _all
    (Classe|BPDlgNPC|OrderOffer _a :InMgr (Variabili|Ottieniunriferimentoasestesso) :From (Variabili|Predefinito|OttieniSelected))))
