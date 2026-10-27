(fn TrAtkSelf (K)
  (Utilità|ControlloDiFlusso|Ramo (Utilità|IsValid (Variabili|Predefinito|OttieniPkWho))
    (:else
      (Funzionedichiamata|TrPeek :A (Utilità|Array|Ottieni(unacopia) (Variabili|Predefinito|OttieniEnL) K))
  (Utilità|ControlloDiFlusso|Ramo (Matematica|Booleano|ANDBoolean (Matematica|Booleano|ANDBoolean (Utility|Operatori|Uguale(==) (Variabili|Predefinito|OttieniPkTgt) (Variabili|Predefinito|OttieniTMe)) (Utility|Operatori|Maggiore(>) (Matematica|Intero|BitwiseAND (Variabili|Predefinito|OttieniPkAtk) (Matematica|Float|Truncate (Variabili|Predefinito|OttieniTP))) 0)) (Matematica|Booleano|ORBoolean (Matematica|Booleano|NOTBoolean (Utility|Operatori|Uguale(==) (Variabili|Predefinito|OttieniTP) 1.0)) (Utility|Operatori|Minoreuguale(<=) (Trasformazione|GetHorizontalDistanceTo (Utilità|Array|Ottieni(unacopia) (Variabili|Predefinito|OttieniEnL) K) (Variabili|Predefinito|OttieniTMe)) 350.0)))
    (:then
      (Variabili|Predefinito|ImpostaPkWho (Variabili|Predefinito|OttieniTMe)))))))
