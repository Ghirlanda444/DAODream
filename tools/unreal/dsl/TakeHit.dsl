(fn TakeHit (Damage)
  (Utilità|ControlloDiFlusso|Ramo (Variabili|Predefinito|OttieniDead)
    (:else
      (Variabili|Predefinito|ImpostaHealth (Utility|Operatori|Sottrai (Variabili|Predefinito|OttieniHealth) Damage))
      (Variabili|Predefinito|ImpostaHealth (Matematica|Float|SelectFloat (Matematica|Float|Max(Float) (Variabili|Predefinito|OttieniHealth) 1.0) (Variabili|Predefinito|OttieniHealth) (Variabili|Predefinito|OttieniImmortal)))
      (Funzionedichiamata|ShowHealthText)
      (Funzionedichiamata|HitFeedback :Damage Damage)
      (Funzionedichiamata|Wounded))))
