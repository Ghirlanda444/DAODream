(fn DropLoot ()
  (Utilità|ControlloDiFlusso|Ramo (Matematica|Booleano|ANDBoolean (Matematica|Booleano|ANDBoolean (Matematica|Booleano|NOTBoolean (Variabili|Predefinito|OttieniInParty)) (Matematica|Booleano|NOTBoolean (Variabili|Predefinito|OttieniDropped))) (Utility|Operatori|Maggioreuguale(>=) (Utilità|Array|Length (Variabili|Predefinito|OttieniNLoot)) 9))
    (:then
      (Variabili|Predefinito|ImpostaDropped "true")
      (Classe|BPPlotManager|DropFor (Variabili|Predefinito|OttieniMgr) :Npc (Variabili|Ottieniunriferimentoasestesso)))))
