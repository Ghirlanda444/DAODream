(fn TrAddValid (A)
  (Utilità|ControlloDiFlusso|Ramo (Utilità|IsValid A)
    (:then
      (Funzionedichiamata|TrPeek :A A)
  (Utilità|ControlloDiFlusso|Ramo (Variabili|Predefinito|OttieniPkAlive)
    (:then
      (Utilità|Array|Add (Variabili|Predefinito|OttieniCL) A))))))
