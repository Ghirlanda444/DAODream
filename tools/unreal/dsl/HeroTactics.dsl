(fn HeroTactics ()
  (Variabili|Predefinito|ImpostaHTDone "false")
  (Variabili|Predefinito|ImpostaHTStop "false")
  (Utilities|FlowControl|ForLoop :FirstIndex 0 :LastIndex (Utility|Operatori|Sottrai (Utility|Operatori|Dividi (Utilità|Array|Length (Variabili|Predefinito|OttieniPTactics)) 6) 1)
    (:LoopBody
      (Funzionedichiamata|HeroTacticRow :I _index))))
