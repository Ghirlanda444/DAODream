(fn ToggleTactics ()
  (Utilità|ControlloDiFlusso|Ramo (Variabili|Predefinito|OttieniTacOpen)
    (:then
      (Funzionedichiamata|CloseTactics))
    (:else
      (Funzionedichiamata|OpenTactics))))
