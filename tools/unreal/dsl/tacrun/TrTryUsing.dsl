(fn TrTryUsing (K)
  (Utilità|ControlloDiFlusso|Ramo (Utilità|IsValid (Variabili|Predefinito|OttieniPkWho))
    (:else
      (Funzionedichiamata|TrPeek :A (Utilità|Array|Ottieni(unacopia) (Variabili|Predefinito|OttieniCL) K))
  (Utilità|ControlloDiFlusso|Ramo (Utility|Operatori|Maggiore(>) (Matematica|Intero|BitwiseAND (Variabili|Predefinito|OttieniPkAtk) (Matematica|Float|Truncate (Variabili|Predefinito|OttieniTP))) 0)
    (:then
      (Variabili|Predefinito|ImpostaPkWho (Utilità|Array|Ottieni(unacopia) (Variabili|Predefinito|OttieniCL) K)))))))
