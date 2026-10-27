(fn TrHated ()
  (Utilità|ControlloDiFlusso|Ramo (Utilità|IsValid (Variabili|Predefinito|OttieniTMeHated))
    (:then
      (Funzionedichiamata|TrPeek :A (Variabili|Predefinito|OttieniTMeHated))
  (Utilità|ControlloDiFlusso|Ramo (Variabili|Predefinito|OttieniPkAlive)
    (:then
      (Variabili|Predefinito|ImpostaPkWho (Variabili|Predefinito|OttieniTMeHated)))))))
