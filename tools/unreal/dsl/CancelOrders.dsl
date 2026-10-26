(fn CancelOrders ()
  (Utilità|ControlloDiFlusso|Ramo (Utilità|IsValid (Variabili|Predefinito|OttieniSelected))
    (:then
      (Classe|BPDlgNPC|DropOrders (Variabili|Predefinito|OttieniSelected)))
    (:else
      (Variabili|Predefinito|ImpostaHeroTarget)
      (Variabili|Predefinito|ImpostaHeroUse)
      (Variabili|Predefinito|ImpostaMoving "false"))))
