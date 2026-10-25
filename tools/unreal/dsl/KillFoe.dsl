(fn KillFoe ()
  (Utilità|ControlloDiFlusso|Ramo (Utility|Operatori|Uguale(==) (Variabili|Predefinito|OttieniFoe) (Gioco|GetPlayerPawn 0))
    (:then
      (Classe|BPPlotManager|HurtPlayer (Variabili|Predefinito|OttieniMgr) :Amount (Utility|Operatori|Aggiungi (Classe|BPPlotManager|OttieniPlayerHealth (Variabili|Predefinito|OttieniMgr)) 1.0)))
    (:else
      (Funzionedichiamata|KillNpcFoe))))
