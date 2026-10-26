(fn OrderOffer (InMgr From)
  (Utilità|ControlloDiFlusso|Ramo (Matematica|Booleano|ANDBoolean (Matematica|Booleano|ANDBoolean (Variabili|Predefinito|OttieniHostile) (Matematica|Booleano|NOTBoolean (Variabili|Predefinito|OttieniDead))) (Matematica|Booleano|ANDBoolean (Matematica|Booleano|NOTBoolean (Variabili|Rendering|OttieniActorHiddenInGame)) (Utility|Operatori|Minore(<) (Trasformazione|GetDistanceTo (Variabili|Ottieniunriferimentoasestesso) From) (Classe|BPPlotManager|OttieniBestDist InMgr))))
    (:then
      (Classe|BPPlotManager|Offer InMgr :Npc (Variabili|Ottieniunriferimentoasestesso) :Dist (Trasformazione|GetDistanceTo (Variabili|Ottieniunriferimentoasestesso) From)))))
