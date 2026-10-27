(fn GAdd (Item N)
  (Variabili|Predefinito|ImpostaGAt -1)
  (Utilities|FlowControl|ForLoop :FirstIndex 0 :LastIndex (Utility|Operatori|Sottrai (Utilità|Array|Length (Variabili|Predefinito|OttieniGItems)) 1)
    (:LoopBody
      (Funzionedichiamata|GFindOne :K _index :Item Item))
    (:Completed
      (Funzionedichiamata|GAddGo :Item Item :N N))))
