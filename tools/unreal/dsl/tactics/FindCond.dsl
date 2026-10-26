(fn FindCond (R)
  (Variabili|Predefinito|ImpostaSCnd (Utilità|Stringa|SelectString "(other)" "" (Utility|Operatori|Maggiore(>) (Utilità|Array|Ottieni(unacopia) (Variabili|Predefinito|OttieniRows) (Utility|Operatori|Aggiungi (Utility|Operatori|Moltiplica R 6) 5)) 0.0)))
  (Utilities|FlowControl|ForLoop :FirstIndex 0 :LastIndex (Utility|Operatori|Sottrai (Utilità|Array|Length (Variabili|Predefinito|OttieniTCondNames)) 1)
    (:LoopBody
      (Funzionedichiamata|MatchCond :R R :K _index))))
