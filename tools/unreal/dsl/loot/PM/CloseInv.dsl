(fn CloseInv ()
  (Utilità|ControlloDiFlusso|Ramo (Variabili|Predefinito|OttieniInvOpen)
    (:then
      (Widget|RemovefromParent (Variabili|Predefinito|OttieniWInv))
      (Variabili|Predefinito|ImpostaInvOpen "false"))))
