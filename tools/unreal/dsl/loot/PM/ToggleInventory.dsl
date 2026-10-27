(fn ToggleInventory ()
  (Utilità|ControlloDiFlusso|Ramo (Variabili|Predefinito|OttieniInvOpen)
    (:then
      (Funzionedichiamata|CloseInv))
    (:else
      (Funzionedichiamata|OpenInv))))
