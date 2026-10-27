(fn TrAtkHated ()
  (Utilità|ControlloDiFlusso|Ramo (Utilità|IsValid (Variabili|Predefinito|OttieniTMeHated))
    (:then
      (Funzionedichiamata|TrPeek :A (Variabili|Predefinito|OttieniTMeHated))
  (Utilità|ControlloDiFlusso|Ramo (Matematica|Booleano|ANDBoolean (Utility|Operatori|Maggiore(>) (Matematica|Intero|BitwiseAND (Variabili|Predefinito|OttieniPkAtk) (Matematica|Float|Truncate (Variabili|Predefinito|OttieniTP))) 0) (Utility|Operatori|Uguale(==) (Variabili|Predefinito|OttieniPkTgt) (Variabili|Predefinito|OttieniTMe)))
    (:then
      (Variabili|Predefinito|ImpostaPkWho (Variabili|Predefinito|OttieniTMe)))))))
