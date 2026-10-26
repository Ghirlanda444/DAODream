(fn ClickOffer (InMgr Where)
  (Utilità|ControlloDiFlusso|Ramo (Matematica|Booleano|ANDBoolean (Matematica|Booleano|NOTBoolean (Variabili|Predefinito|OttieniDead)) (Matematica|Booleano|NOTBoolean (Variabili|Rendering|OttieniActorHiddenInGame)))
    (:then
      (Classe|BPPlotManager|PickOffer InMgr :Npc (Variabili|Ottieniunriferimentoasestesso) :Where Where))))
