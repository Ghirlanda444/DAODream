(fn CommandRoute (Where What)
  (Utilità|ControlloDiFlusso|Ramo (Utilità|IsValid (Variabili|Predefinito|OttieniPickNpc))
    (:then
      (Funzionedichiamata|CommandNpc :Where Where))
    (:else
      (Funzionedichiamata|CommandThing :Where Where :What What))))
