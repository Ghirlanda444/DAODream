(fn TrGatherOne (A)
  (Utilità|ControlloDiFlusso|Ramo (Utility|Operatori|Uguale(==) A (Variabili|Predefinito|OttieniTMe))
    (:else
      (Funzionedichiamata|TrPeek :A A)
  (Utilità|ControlloDiFlusso|Ramo (Variabili|Predefinito|OttieniPkVis)
    (:then
      (Funzionedichiamata|TrSort :A A))))))
