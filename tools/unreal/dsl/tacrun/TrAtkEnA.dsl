(fn TrAtkEnA (K)
  (Utilità|ControlloDiFlusso|Ramo (Utilità|IsValid (Variabili|Predefinito|OttieniPkWho))
    (:else
      (Funzionedichiamata|TrPeek :A (Utilità|Array|Ottieni(unacopia) (Variabili|Predefinito|OttieniAllyL) K))
  (Utilità|ControlloDiFlusso|Ramo (Matematica|Booleano|ANDBoolean (Matematica|Booleano|ANDBoolean (Utility|Operatori|Uguale(==) (Variabili|Predefinito|OttieniPkTgt) (Variabili|Predefinito|OttieniPkMem)) (Utility|Operatori|Maggiore(>) (Matematica|Intero|BitwiseAND (Variabili|Predefinito|OttieniPkAtk) (Matematica|Float|Truncate (Variabili|Predefinito|OttieniTP))) 0)) (Matematica|Booleano|ORBoolean (Matematica|Booleano|NOTBoolean (Utility|Operatori|Uguale(==) (Variabili|Predefinito|OttieniTP) 1.0)) (Utility|Operatori|Minoreuguale(<=) (Trasformazione|GetHorizontalDistanceTo (Utilità|Array|Ottieni(unacopia) (Variabili|Predefinito|OttieniAllyL) K) (Variabili|Predefinito|OttieniPkMem)) 350.0)))
    (:then
      (Variabili|Predefinito|ImpostaPkWho (Variabili|Predefinito|OttieniPkMem)))))))
