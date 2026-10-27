(fn CdCheck (Who Ab)
  (Variabili|Predefinito|ImpostaGBool "true")
  (Utilities|FlowControl|ForLoop :FirstIndex 0 :LastIndex (Utility|Operatori|Sottrai (Utilità|Array|Length (Variabili|Predefinito|OttieniCdWho)) 1)
    (:LoopBody
      (Funzionedichiamata|CdOne :K _index :Who Who :Ab Ab))))
