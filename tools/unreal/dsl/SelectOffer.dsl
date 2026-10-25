(fn SelectOffer (InMgr)
  (Utilità|ControlloDiFlusso|Ramo (Matematica|Booleano|ANDBoolean (Matematica|Booleano|ANDBoolean (Variabili|Predefinito|OttieniInParty) (Matematica|Booleano|NOTBoolean (Variabili|Predefinito|OttieniDead))) (Matematica|Booleano|NOTBoolean (Variabili|Rendering|OttieniActorHiddenInGame)))
    (:then
      (Classe|BPPlotManager|MemberOffer InMgr :Npc (Variabili|Ottieniunriferimentoasestesso)))))
