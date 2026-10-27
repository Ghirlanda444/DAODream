(fn CloseLootUI ()
  (Utilità|ControlloDiFlusso|Ramo (Variabili|Predefinito|OttieniLootOpen)
    (:then
      (Widget|RemovefromParent (Variabili|Predefinito|OttieniWLoot))
      (Variabili|Predefinito|ImpostaLootOpen "false"))))
