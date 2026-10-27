(fn InvAdd (Item N)
  (Utilità|ControlloDiFlusso|Ramo (Utility|Operatori|Uguale(==) (Utilità|Array|Ottieni(unacopia) (Variabili|Predefinito|OttieniItemStats) (Utility|Operatori|Aggiungi (Utility|Operatori|Moltiplica Item 6) 0)) 4.0)
    (:then
      (Variabili|Predefinito|ImpostaMoney (Utility|Operatori|Aggiungi (Variabili|Predefinito|OttieniMoney) N)))
    (:else
      (Funzionedichiamata|InvFind :Item Item)
      (Funzionedichiamata|InvAddGo :Item Item :N N))))
