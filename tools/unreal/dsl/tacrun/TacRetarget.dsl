(fn TacRetarget ()
  (Variabili|Predefinito|ImpostaFoe (Variabili|Predefinito|OttieniTacWho))
  (Funzionedichiamata|TacTooFar)
  (Utilità|ControlloDiFlusso|Ramo (Variabili|Predefinito|OttieniInParty)
    (:then
      (Funzionedichiamata|TacSetTarget))))
