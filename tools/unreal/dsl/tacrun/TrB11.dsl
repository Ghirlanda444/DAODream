(fn TrB11 ()
  (Funzionedichiamata|TrMember)
  (Utilità|ControlloDiFlusso|Ramo (Utilità|IsValid (Variabili|Predefinito|OttieniPkMem))
    (:then
      (Funzionedichiamata|TrPeek :A (Variabili|Predefinito|OttieniPkMem))
  (Utilità|ControlloDiFlusso|Ramo (Utilità|IsValid (Variabili|Predefinito|OttieniPkTgt))
    (:then
      (Variabili|Predefinito|ImpostaPkWho (Variabili|Predefinito|OttieniPkTgt)))))))
