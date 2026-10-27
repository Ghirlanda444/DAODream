(fn FindAct (R)
  (Variabili|Predefinito|ImpostaSCmd "?")
  (Utilities|FlowControl|ForLoop :FirstIndex 0 :LastIndex (Utility|Operatori|Sottrai (Utility|Operatori|Dividi (Utilità|Array|Length (Variabili|Predefinito|OttieniTCmds)) (Utility|Operatori|Aggiungi (Utilità|Array|Length (Variabili|Predefinito|OttieniTTargetNames)) 1)) 1)
    (:LoopBody
      (Funzionedichiamata|MatchCmd :C (Utilità|Array|Ottieni(unacopia) (Variabili|Predefinito|OttieniRows) (Utility|Operatori|Aggiungi (Utility|Operatori|Moltiplica R 6) 3)) :K _index))
    (:Completed
      (Variabili|Predefinito|ImpostaSAct (Utilità|Stringa|SelectString (Variabili|Predefinito|OttieniSCmd) "" (Utility|Operatori|Maggiore(>) (Utilità|Array|Ottieni(unacopia) (Variabili|Predefinito|OttieniRows) (Utility|Operatori|Aggiungi (Utility|Operatori|Moltiplica R 6) 5)) 0.0)))
      (Funzionedichiamata|ActDetail :R R))))
