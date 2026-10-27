(fn HealWho (A)
  (Utilità|ControlloDiFlusso|Ramo (Utility|Operatori|Uguale(==) A (Gioco|GetPlayerPawn 0))
    (:then
      (Classe|BPPlotManager|HealPlayer (Variabili|Predefinito|OttieniMgr) :Amount (Variabili|Predefinito|OttieniHealAmt)))
    (:else
      (Funzionedichiamata|HealCast :A A))))
