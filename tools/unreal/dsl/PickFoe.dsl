(fn PickFoe (Hostile)
  (Funzionedichiamata|CountAttackers :Hostile Hostile)
  (Variabili|Predefinito|ImpostaFoeDist 1500.0)
  (Variabili|Predefinito|ImpostaFoeBest)
  (Funzionedichiamata|OfferPlayer :Hostile Hostile)
  (bind _all (Attore|GetAllActorsOfClass "/Game/Cousland/Dialogue/BP_DlgNPC.BP_DlgNPC_C"))
  (for _a _all
    (Classe|BPDlgNPC|FoeBid _a :InMgr (Variabili|Ottieniunriferimentoasestesso) :Hostile Hostile))
  (Classe|BPDlgNPC|SetFoe Hostile :InFoe (Variabili|Predefinito|OttieniFoeBest)))
