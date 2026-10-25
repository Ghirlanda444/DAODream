(fn SeePlayer ()
  (Utilità|ControlloDiFlusso|Ramo (Matematica|Booleano|ANDBoolean (Matematica|Booleano|NOTBoolean (Matematica|Booleano|ORBoolean (Classe|BPPlotManager|OttieniPlayerDown (Variabili|Predefinito|OttieniMgr)) (Classe|BPPlotManager|OttieniFeign (Variabili|Predefinito|OttieniMgr)))) (Matematica|Booleano|ANDBoolean (Utility|Operatori|Minoreuguale(<=) (Trasformazione|GetDistanceTo (Variabili|Ottieniunriferimentoasestesso) (Gioco|GetPlayerPawn 0)) 1500.0) (Utility|Operatori|Minore(<) (Utilità|Array|FindItem (Variabili|Predefinito|OttieniThreatWho) (Gioco|GetPlayerPawn 0)) 0)))
    (:then
      (Funzionedichiamata|AddThreat :Who (Gioco|GetPlayerPawn 0) :Amount (Classe|BPPlotManager|OttieniPSeen (Variabili|Predefinito|OttieniMgr))))))
