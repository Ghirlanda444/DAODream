(fn DropDownFoe ()
  (Funzionedichiamata|WhoUp :Who (Variabili|Predefinito|OttieniFoe))
  (Utilità|ControlloDiFlusso|Ramo (Matematica|Booleano|ANDBoolean (Utilità|IsValid (Variabili|Predefinito|OttieniFoe)) (Matematica|Booleano|NOTBoolean (Variabili|Predefinito|OttieniWhoOk)))
    (:then
      (Variabili|Predefinito|ImpostaFoe))))
