(fn TakeHit (Damage)
  (Utilità|ControlloDiFlusso|Ramo (Variabili|Predefinito|OttieniDead)
    (:else
      (Variabili|Predefinito|ImpostaHealth (Utility|Operatori|Sottrai (Variabili|Predefinito|OttieniHealth) Damage))
      (Funzionedichiamata|ShowHealthText)
      (Funzionedichiamata|HitFeedback :Damage Damage)
      (Funzionedichiamata|Wounded))))
