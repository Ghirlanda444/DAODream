(fn RunQueuedAttack ()
  (Utilità|ControlloDiFlusso|Ramo (Variabili|Predefinito|OttieniQueuedAttack)
    (:then
      (Variabili|Predefinito|ImpostaQueuedAttack "false")
      (Funzionedichiamata|PlayerAttackNow))))
