(fn CountAround ()
  (Classe|BPPlotManager|ResetAround (Variabili|Predefinito|OttieniMgr))
  (bind _all (Attore|GetAllActorsOfClass "/Game/Cousland/Dialogue/BP_DlgNPC.BP_DlgNPC_C"))
  (for _a _all
    (Funzionedichiamata|AroundOffer _a :From (Variabili|Ottieniunriferimentoasestesso) :bPartySide (Variabili|Predefinito|OttieniInParty) :InMgr (Variabili|Predefinito|OttieniMgr)))
  (Funzionedichiamata|AroundPlayer)
  (Variabili|Predefinito|ImpostaAround (Classe|BPPlotManager|OttieniAroundCount (Variabili|Predefinito|OttieniMgr))))
