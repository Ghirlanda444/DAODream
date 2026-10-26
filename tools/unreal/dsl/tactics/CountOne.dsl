(fn CountOne (K)
  (Utilità|ControlloDiFlusso|Ramo (Utility|Operatori|Uguale(==) (Utilità|Array|Ottieni(unacopia) (Variabili|Predefinito|OttieniTConds) (Utility|Operatori|Aggiungi (Utility|Operatori|Moltiplica K 3) 1)) (Variabili|Predefinito|OttieniBaseId))
    (:then
      (Variabili|Predefinito|ImpostaNB (Utility|Operatori|Aggiungi (Variabili|Predefinito|OttieniNB) 1))
      (Variabili|Predefinito|ImpostaLastCK K))))
