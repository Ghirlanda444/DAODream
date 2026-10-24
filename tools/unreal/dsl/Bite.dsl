(fn Bite (Dt)
  (Variabili|Predefinito|ImpostaAttackTimer (Utility|Operatori|Sottrai (Variabili|Predefinito|OttieniAttackTimer) Dt))
  (Utilità|ControlloDiFlusso|Ramo (Utility|Operatori|Maggiore(>) (Variabili|Predefinito|OttieniAttackTimer) 0.0)
    (:else
      (Variabili|Predefinito|ImpostaAttackTimer (Variabili|Predefinito|OttieniInterval))
      (Funzionedichiamata|PlayAttackAnim)
      (Funzionedichiamata|StrikeFoe))))
