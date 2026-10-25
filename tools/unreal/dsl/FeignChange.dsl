(fn FeignChange ()
  (Variabili|Predefinito|ImpostaFeignStart (Matematica|Booleano|ANDBoolean (Variabili|Predefinito|OttieniFeign) (Matematica|Booleano|NOTBoolean (Variabili|Predefinito|OttieniWasFeign))))
  (Variabili|Predefinito|ImpostaWasFeign (Variabili|Predefinito|OttieniFeign))
  (Utilità|ControlloDiFlusso|Ramo (Variabili|Predefinito|OttieniFeignStart)
    (:then
      (Funzionedichiamata|ForgetPlayerAll))))
