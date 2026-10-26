(fn AddCondOpt (K)
  (Utilità|ControlloDiFlusso|Ramo (Utility|Operatori|Uguale(==) (Utilità|Array|Ottieni(unacopia) (Variabili|Predefinito|OttieniTConds) (Utility|Operatori|Aggiungi (Utility|Operatori|Moltiplica K 3) 1)) (Variabili|Predefinito|OttieniBaseId))
    (:then
      (Utilità|Array|Add (Variabili|Predefinito|OttieniOptIds) K)
      (Utilità|Array|Add (Variabili|Predefinito|OttieniOptNames) (Utilità|Array|Ottieni(unacopia) (Variabili|Predefinito|OttieniTCondNames) K)))))
