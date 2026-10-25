(fn LockFoe (Seconds)
  (Utilità|ControlloDiFlusso|Ramo (Utility|Operatori|Uguale(==) (Variabili|Predefinito|OttieniFoe) (Gioco|GetPlayerPawn 0))
    (:then
      (Classe|BPPlotManager|LockPlayer (Variabili|Predefinito|OttieniMgr) :Seconds Seconds))
    (:else
      (Funzionedichiamata|SlowNpcFoe :Seconds Seconds))))
