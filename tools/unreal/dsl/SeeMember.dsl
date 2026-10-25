(fn SeeMember (Npc)
  (Classe|BPPlotManager|Inspect (Variabili|Predefinito|OttieniMgr) :Npc Npc :Asker (Variabili|Ottieniunriferimentoasestesso))
  (Utilità|ControlloDiFlusso|Ramo (Matematica|Booleano|ANDBoolean (Matematica|Booleano|ANDBoolean (Variabili|Predefinito|OttieniInspParty) (Variabili|Predefinito|OttieniWhoOk)) (Matematica|Booleano|ANDBoolean (Utility|Operatori|Minoreuguale(<=) (Trasformazione|GetDistanceTo (Variabili|Ottieniunriferimentoasestesso) Npc) 1500.0) (Utility|Operatori|Minore(<) (Utilità|Array|FindItem (Variabili|Predefinito|OttieniThreatWho) Npc) 0)))
    (:then
      (Funzionedichiamata|AddThreat :Who Npc :Amount (Variabili|Predefinito|OttieniInspSeen)))))
