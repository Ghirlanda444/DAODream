(fn DropOrders ()
  (Variabili|Predefinito|ImpostaOrderTarget)
  (Variabili|Predefinito|ImpostaOrderMove "false")
  (Utilità|ControlloDiFlusso|Ramo (Variabili|Predefinito|OttieniControlled)
    (:then
      (Variabili|Predefinito|ImpostaTarget))))
