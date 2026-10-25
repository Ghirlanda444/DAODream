(fn DisarmFoe (Seconds)
  (Utilità|ControlloDiFlusso|Ramo (Utility|Operatori|Uguale(==) (Variabili|Predefinito|OttieniFoe) (Gioco|GetPlayerPawn 0))
    (:then
      (Classe|BPPlotManager|DisarmPlayer (Variabili|Predefinito|OttieniMgr) :Seconds Seconds))
    (:else
      (Funzionedichiamata|DisarmNpcFoe :Seconds Seconds))))
