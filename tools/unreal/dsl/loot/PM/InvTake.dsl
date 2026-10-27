(fn InvTake (Slot N)
  (Utilità|Array|SetArrayElem (Variabili|Predefinito|OttieniInvN) Slot (Utility|Operatori|Sottrai (Utilità|Array|Ottieni(unacopia) (Variabili|Predefinito|OttieniInvN) Slot) N))
  (Utilità|ControlloDiFlusso|Ramo (Utility|Operatori|Minoreuguale(<=) (Utilità|Array|Ottieni(unacopia) (Variabili|Predefinito|OttieniInvN) Slot) 0)
    (:then
      (Utilità|Array|RemoveIndex (Variabili|Predefinito|OttieniInv) Slot)
      (Utilità|Array|RemoveIndex (Variabili|Predefinito|OttieniInvN) Slot))))
