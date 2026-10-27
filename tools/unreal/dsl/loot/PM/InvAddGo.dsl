(fn InvAddGo (Item N)
  (Utilità|ControlloDiFlusso|Ramo (Utility|Operatori|Maggioreuguale(>=) (Variabili|Predefinito|OttieniInvAt) 0)
    (:then
      (Utilità|Array|SetArrayElem (Variabili|Predefinito|OttieniInvN) (Variabili|Predefinito|OttieniInvAt) (Utility|Operatori|Aggiungi (Utilità|Array|Ottieni(unacopia) (Variabili|Predefinito|OttieniInvN) (Variabili|Predefinito|OttieniInvAt)) N)))
    (:else
      (Utilità|Array|Add (Variabili|Predefinito|OttieniInv) Item)
      (Utilità|Array|Add (Variabili|Predefinito|OttieniInvN) N))))
