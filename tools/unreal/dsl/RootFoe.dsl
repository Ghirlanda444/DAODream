(fn RootFoe (Seconds)
  (Utilità|ControlloDiFlusso|Ramo (Utility|Operatori|Uguale(==) (Variabili|Predefinito|OttieniFoe) (Gioco|GetPlayerPawn 0))
    (:then
      (Classe|BPPlotManager|RootPlayer (Variabili|Predefinito|OttieniMgr) :Seconds Seconds))
    (:else
      (Funzionedichiamata|RootNpcFoe :Seconds Seconds))))
