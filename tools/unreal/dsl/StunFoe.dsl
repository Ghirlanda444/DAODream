(fn StunFoe (Seconds bFall)
  (Utilità|ControlloDiFlusso|Ramo (Utility|Operatori|Uguale(==) (Variabili|Predefinito|OttieniFoe) (Gioco|GetPlayerPawn 0))
    (:then
      (Classe|BPPlotManager|StunPlayer (Variabili|Predefinito|OttieniMgr) :Seconds Seconds :bFall bFall))
    (:else
      (Funzionedichiamata|StunNpcFoe :Seconds Seconds :bFall bFall))))
