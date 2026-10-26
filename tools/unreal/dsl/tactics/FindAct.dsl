(fn FindAct (R)
  (Variabili|Predefinito|ImpostaSAct (Utilità|Stringa|SelectString (Variabili|Predefinito|OttieniAttackName) (Utilità|Stringa|SelectString "?" "" (Utility|Operatori|Maggiore(>) (Utilità|Array|Ottieni(unacopia) (Variabili|Predefinito|OttieniRows) (Utility|Operatori|Aggiungi (Utility|Operatori|Moltiplica R 6) 5)) 0.0)) (Matematica|Booleano|ANDBoolean (Utility|Operatori|Maggiore(>) (Utilità|Array|Ottieni(unacopia) (Variabili|Predefinito|OttieniRows) (Utility|Operatori|Aggiungi (Utility|Operatori|Moltiplica R 6) 5)) 0.0) (Utility|Operatori|Uguale(==) (Utilità|Array|Ottieni(unacopia) (Variabili|Predefinito|OttieniRows) (Utility|Operatori|Aggiungi (Utility|Operatori|Moltiplica R 6) 3)) 2.0))))
  (Utilities|FlowControl|ForLoop :FirstIndex 0 :LastIndex (Utility|Operatori|Sottrai (Utilità|Array|Length (Variabili|Predefinito|OttieniTalNames)) 1)
    (:LoopBody
      (Funzionedichiamata|MatchAct :R R :K _index))))
