(fn SetHold (bOn)
  (Utilità|ControlloDiFlusso|Ramo (Variabili|Predefinito|OttieniInParty)
    (:then
      (Variabili|Predefinito|ImpostaHold bOn)
      (Funzionedichiamata|SayText :Txt (Utilità|Stringa|SelectString "Holding" "Following" bOn)))))
