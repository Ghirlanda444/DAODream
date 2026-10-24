(fn FoeOffer (Cand Dist)
  (Utilità|ControlloDiFlusso|Ramo (Utility|Operatori|Minore(<) Dist (Variabili|Predefinito|OttieniFoeDist))
    (:then
      (Variabili|Predefinito|ImpostaFoeDist Dist)
      (Variabili|Predefinito|ImpostaFoeBest Cand))))
