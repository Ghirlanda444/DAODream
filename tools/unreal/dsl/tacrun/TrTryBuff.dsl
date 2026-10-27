(fn TrTryBuff (K)
  (Utilità|ControlloDiFlusso|Ramo (Utilità|IsValid (Variabili|Predefinito|OttieniPkWho))
    (:else
      (Funzionedichiamata|TrPeek :A (Utilità|Array|Ottieni(unacopia) (Variabili|Predefinito|OttieniCL) K))
      (Funzionedichiamata|TrBuffOf :A (Utilità|Array|Ottieni(unacopia) (Variabili|Predefinito|OttieniCL) K))
  (Utilità|ControlloDiFlusso|Ramo (Matematica|Booleano|ANDBoolean (Variabili|Predefinito|OttieniPkBuff) (Matematica|Booleano|ORBoolean (Utility|Operatori|Uguale(==) (Variabili|Predefinito|OttieniTP) 0.0) (Utility|Operatori|Minoreuguale(<=) (Trasformazione|GetHorizontalDistanceTo (Variabili|Predefinito|OttieniTMe) (Utilità|Array|Ottieni(unacopia) (Variabili|Predefinito|OttieniCL) K)) (Matematica|Float|SelectFloat 350.0 (Matematica|Float|SelectFloat 1200.0 (Matematica|Float|SelectFloat 8000.0 1000000.0 (Utility|Operatori|Uguale(==) (Variabili|Predefinito|OttieniTP) 3.0)) (Utility|Operatori|Uguale(==) (Variabili|Predefinito|OttieniTP) 2.0)) (Utility|Operatori|Uguale(==) (Variabili|Predefinito|OttieniTP) 1.0)))))
    (:then
      (Variabili|Predefinito|ImpostaPkWho (Utilità|Array|Ottieni(unacopia) (Variabili|Predefinito|OttieniCL) K)))))))
