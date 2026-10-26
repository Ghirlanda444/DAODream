(fn CloseTactics ()
  (Widget|RemovefromParent (Variabili|Predefinito|OttieniTac))
  (Variabili|Predefinito|ImpostaTacOpen "false")
  (Utilità|ControlloDiFlusso|Ramo (Matematica|Booleano|ANDBoolean (Variabili|Predefinito|OttieniPaused) (Matematica|Booleano|NOTBoolean (Variabili|Predefinito|OttieniTacPaused)))
    (:then
      (Funzionedichiamata|TogglePause))))
