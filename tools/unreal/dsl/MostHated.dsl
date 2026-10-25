(fn MostHated ()
  (Variabili|Predefinito|ImpostaHateBest -1.0)
  (Variabili|Predefinito|ImpostaHated)
  (Utilities|FlowControl|ForLoop :FirstIndex 0 :LastIndex (Utility|Operatori|Sottrai (Utilità|Array|Length (Variabili|Predefinito|OttieniThreatWho)) 1)
    (:LoopBody
      (Funzionedichiamata|HateCheck :I _index))))
