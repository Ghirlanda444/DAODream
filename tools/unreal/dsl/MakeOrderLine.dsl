(fn MakeOrderLine ()
  (Variabili|Predefinito|ImpostaOrderLine (Utilità|Stringa|Append (Variabili|Predefinito|OttieniDisplayName) (Utilità|Stringa|SelectString " (holding):  " ":  " (Variabili|Predefinito|OttieniHold))))
  (Utilities|FlowControl|ForLoop :FirstIndex 0 :LastIndex 5
    (:LoopBody
      (Funzionedichiamata|AddOrderSlot :K _index))))
