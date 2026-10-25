(fn ArmourFoe (Amount Seconds)
  (Utilità|ControlloDiFlusso|Ramo (Utility|Operatori|Uguale(==) (Variabili|Predefinito|OttieniFoe) (Gioco|GetPlayerPawn 0))
    (:then
      (Classe|BPPlotManager|ArmourPlayer (Variabili|Predefinito|OttieniMgr) :Amount Amount :Seconds Seconds))
    (:else
      (Funzionedichiamata|ArmourNpcFoe :Amount Amount :Seconds Seconds))))
