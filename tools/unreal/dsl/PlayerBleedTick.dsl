(fn PlayerBleedTick (Dt)
  (Utilità|ControlloDiFlusso|Ramo (Matematica|Booleano|ANDBoolean (Utility|Operatori|Maggiore(>) (Variabili|Predefinito|OttieniPBleedUntil) (Utilità|Testo|GetGameTimeinSeconds)) (Matematica|Booleano|NOTBoolean (Variabili|Predefinito|OttieniPlayerDown)))
    (:then
      (Funzionedichiamata|HurtPlayer :Amount (Utility|Operatori|Moltiplica (Variabili|Predefinito|OttieniPBleedRate) Dt)))))
