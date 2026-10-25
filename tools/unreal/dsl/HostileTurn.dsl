(fn HostileTurn (Dt)
  (Variabili|Predefinito|ImpostaFoeTimer (Utility|Operatori|Sottrai (Variabili|Predefinito|OttieniFoeTimer) Dt))
  (Utilità|ControlloDiFlusso|Ramo (Utility|Operatori|Maggiore(>) (Variabili|Predefinito|OttieniFoeTimer) 0.0)
    (:then
      (Funzionedichiamata|FoeStep :Dt Dt))
    (:else
      (Variabili|Predefinito|ImpostaFoeTimer 0.5)
      (Funzionedichiamata|ThreatPick)
      (Funzionedichiamata|FoeStep :Dt Dt))))
