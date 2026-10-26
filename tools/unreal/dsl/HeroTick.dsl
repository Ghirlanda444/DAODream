(fn HeroTick (Dt)
  (Utilità|ControlloDiFlusso|Ramo (Matematica|Booleano|ORBoolean (Variabili|Predefinito|OttieniTalking) (Matematica|Booleano|ORBoolean (Variabili|Predefinito|OttieniPlayerDown) (Variabili|Predefinito|OttieniGameOver)))
    (:then
      (Funzionedichiamata|CancelOrders))
    (:else
      (Funzionedichiamata|KeepCursor)
      (Funzionedichiamata|HeroOrderStep :Dt Dt))))
