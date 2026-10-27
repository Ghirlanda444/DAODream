(fn SupportTick (Dt)
  (Variabili|Predefinito|ImpostaSupportTimer (Utility|Operatori|Sottrai (Variabili|Predefinito|OttieniSupportTimer) Dt))
  (Utilità|ControlloDiFlusso|Ramo (Matematica|Booleano|ORBoolean (Variabili|Predefinito|OttieniControlled) (Utility|Operatori|Maggiore(>) (Variabili|Predefinito|OttieniSupportTimer) 0.0))
    (:else
      (Variabili|Predefinito|ImpostaSupportTimer (Variabili|Predefinito|OttieniInterval))
      (Funzionedichiamata|SupportRound))))
