(fn FindTarget (R)
  (Variabili|Predefinito|ImpostaSTgt (Utilità|Stringa|SelectString "?" "(empty)" (Utility|Operatori|Maggiore(>) (Utilità|Array|Ottieni(unacopia) (Variabili|Predefinito|OttieniRows) (Utility|Operatori|Aggiungi (Utility|Operatori|Moltiplica R 6) 5)) 0.0)))
  (Utilities|FlowControl|ForLoop :FirstIndex 0 :LastIndex (Utility|Operatori|Sottrai (Utilità|Array|Length (Variabili|Predefinito|OttieniTTargetNames)) 1)
    (:LoopBody
      (Funzionedichiamata|MatchTarget :R R :K _index))
    (:Completed
      (Funzionedichiamata|FindMemberTgt :R R))))
