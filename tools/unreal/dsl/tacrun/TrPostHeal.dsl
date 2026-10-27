(fn TrPostHeal ()
  (Utilità|ControlloDiFlusso|Ramo (Matematica|Booleano|ANDBoolean (Matematica|Booleano|ANDBoolean (Matematica|Booleano|ANDBoolean (Utility|Operatori|Uguale(==) (Variabili|Predefinito|OttieniTT) 1.0) (Utility|Operatori|Uguale(==) (Variabili|Predefinito|OttieniTC) 4.0)) (Utility|Operatori|Uguale(==) (Variabili|Predefinito|OttieniTS) 10104.0)) (Utilità|IsValid (Variabili|Predefinito|OttieniPkWho)))
    (:then
      (Funzionedichiamata|TrPeek :A (Variabili|Predefinito|OttieniTMe))
  (Utilità|ControlloDiFlusso|Ramo (Utility|Operatori|Maggioreuguale(>=) (Variabili|Predefinito|OttieniPkHp) (Variabili|Predefinito|OttieniPkMax))
    (:then
      (Variabili|Predefinito|ImpostaPkWho))))))
