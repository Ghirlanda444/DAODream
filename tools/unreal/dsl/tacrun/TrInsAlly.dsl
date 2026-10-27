(fn TrInsAlly (A D)
  (Variabili|Predefinito|ImpostaPkIns 0)
  (Utilities|FlowControl|ForLoop :FirstIndex 0 :LastIndex (Utility|Operatori|Sottrai (Utilità|Array|Length (Variabili|Predefinito|OttieniAllyD)) 1)
    (:LoopBody
      (Funzionedichiamata|TrInsAllyLess :K _index :D D))
    (:Completed
      (Utilità|Array|Insert (Variabili|Predefinito|OttieniAllyL) A (Variabili|Predefinito|OttieniPkIns))
      (Utilità|Array|Insert (Variabili|Predefinito|OttieniAllyD) D (Variabili|Predefinito|OttieniPkIns)))))
