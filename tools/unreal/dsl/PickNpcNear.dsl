(fn PickNpcNear (Where)
  (Variabili|Predefinito|ImpostaPickNpc)
  (Variabili|Predefinito|ImpostaPickDist 100.0)
  (bind _all (Attore|GetAllActorsOfClass "/Game/Cousland/Dialogue/BP_DlgNPC.BP_DlgNPC_C"))
  (for _a _all
    (Classe|BPDlgNPC|ClickOffer _a :InMgr (Variabili|Ottieniunriferimentoasestesso) :Where Where)))
