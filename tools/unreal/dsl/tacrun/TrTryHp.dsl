(fn TrTryHp (K)
  (Utilità|ControlloDiFlusso|Ramo (Utilità|IsValid (Variabili|Predefinito|OttieniPkWho))
    (:else
      (Funzionedichiamata|TrPeek :A (Utilità|Array|Ottieni(unacopia) (Variabili|Predefinito|OttieniCL) K))
  (Utilità|ControlloDiFlusso|Ramo (Matematica|Booleano|ORBoolean (Matematica|Booleano|ANDBoolean (Utility|Operatori|Minore(<) (Variabili|Predefinito|OttieniTP) 0.0) (Utility|Operatori|Minore(<) (Variabili|Predefinito|OttieniPkPct) (Utility|Operatori|Moltiplica (Variabili|Predefinito|OttieniTP) -1.0))) (Matematica|Booleano|ANDBoolean (Utility|Operatori|Maggioreuguale(>=) (Variabili|Predefinito|OttieniTP) 0.0) (Utility|Operatori|Maggioreuguale(>=) (Variabili|Predefinito|OttieniPkPct) (Variabili|Predefinito|OttieniTP))))
    (:then
      (Variabili|Predefinito|ImpostaPkWho (Utilità|Array|Ottieni(unacopia) (Variabili|Predefinito|OttieniCL) K)))))))
