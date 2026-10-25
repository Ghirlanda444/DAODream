(fn PlayerAttack ()
  (Utilità|ControlloDiFlusso|Ramo (Utilità|IsValid (Variabili|Predefinito|OttieniSelected))
    (:then
      (Funzionedichiamata|OrderAttack))
    (:else
      (Utilità|ControlloDiFlusso|Ramo (Variabili|Predefinito|OttieniPaused)
        (:then
          (Variabili|Predefinito|ImpostaQueuedAttack "true")
          (Funzionedichiamata|ShowMsg :Txt "Paused: attack queued"))
        (:else
          (Funzionedichiamata|PlayerAttackNow))))))
