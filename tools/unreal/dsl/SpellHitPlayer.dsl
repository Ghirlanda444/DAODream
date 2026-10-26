(fn SpellHitPlayer (Amount)
  (Utilità|ControlloDiFlusso|Ramo (Matematica|Booleano|ORBoolean (Matematica|Booleano|ORBoolean (Variabili|Predefinito|OttieniTalking) (Variabili|Predefinito|OttieniGameOver)) (Variabili|Predefinito|OttieniPlayerDown))
    (:else
      (Variabili|Predefinito|ImpostaLastDamage Amount)
      (Funzionedichiamata|HurtPlayer :Amount Amount))))
