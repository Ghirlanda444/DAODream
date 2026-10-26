(fn AroundOffer (From bPartySide InMgr)
  (Utilità|ControlloDiFlusso|Ramo (Matematica|Booleano|ANDBoolean (Matematica|Booleano|ANDBoolean (Matematica|Booleano|ANDBoolean (Matematica|Booleano|NOTBoolean (Variabili|Predefinito|OttieniDead)) (Matematica|Booleano|NOTBoolean (Variabili|Rendering|OttieniActorHiddenInGame))) (Matematica|Booleano|ORBoolean (Matematica|Booleano|ANDBoolean bPartySide (Variabili|Predefinito|OttieniHostile)) (Matematica|Booleano|ANDBoolean (Matematica|Booleano|NOTBoolean bPartySide) (Variabili|Predefinito|OttieniInParty)))) (Utility|Operatori|Minore(<) (Trasformazione|GetDistanceTo (Variabili|Ottieniunriferimentoasestesso) From) 250.0))
    (:then
      (Classe|BPPlotManager|AroundOne InMgr))))
