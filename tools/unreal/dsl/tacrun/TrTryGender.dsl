(fn TrTryGender (K)
  (Utilità|ControlloDiFlusso|Ramo (Utilità|IsValid (Variabili|Predefinito|OttieniPkWho))
    (:else
      (Funzionedichiamata|TrPeek :A (Utilità|Array|Ottieni(unacopia) (Variabili|Predefinito|OttieniCL) K))
  (Utilità|ControlloDiFlusso|Ramo (Utility|Operatori|Uguale(==) (Matematica|Conversioni|ToFloat(Integer) (Variabili|Predefinito|OttieniPkGender)) (Variabili|Predefinito|OttieniTP))
    (:then
      (Variabili|Predefinito|ImpostaPkWho (Utilità|Array|Ottieni(unacopia) (Variabili|Predefinito|OttieniCL) K)))))))
