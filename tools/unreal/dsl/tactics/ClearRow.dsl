(fn ClearRow (R)
  (Variabili|Predefinito|ImpostaEditRow R)
  (Utilities|FlowControl|ForLoop :FirstIndex 0 :LastIndex 5
    (:LoopBody
      (Funzionedichiamata|ZeroCell :J _index))
    (:Completed
      (Funzionedichiamata|Done))))
