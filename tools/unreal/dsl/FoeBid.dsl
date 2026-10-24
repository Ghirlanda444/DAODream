(fn FoeBid (InMgr Hostile)
  (Utilità|ControlloDiFlusso|Ramo (Matematica|Booleano|ANDBoolean (Matematica|Booleano|ANDBoolean (Variabili|Predefinito|OttieniInParty) (Matematica|Booleano|NOTBoolean (Variabili|Predefinito|OttieniDead))) (Matematica|Booleano|NOTBoolean (Variabili|Rendering|OttieniActorHiddenInGame)))
    (:then
      (Classe|BPPlotManager|FoeOffer InMgr :Cand (Variabili|Ottieniunriferimentoasestesso) :Dist (Trasformazione|GetHorizontalDistanceTo (Variabili|Ottieniunriferimentoasestesso) Hostile)))))
