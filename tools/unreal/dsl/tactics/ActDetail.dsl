(fn ActDetail (R)
  (Utilità|ControlloDiFlusso|Ramo (Matematica|Booleano|ANDBoolean (Utility|Operatori|Maggiore(>) (Utilità|Array|Ottieni(unacopia) (Variabili|Predefinito|OttieniRows) (Utility|Operatori|Aggiungi (Utility|Operatori|Moltiplica R 6) 5)) 0.0) (Utility|Operatori|Uguale(==) (Utilità|Array|Ottieni(unacopia) (Variabili|Predefinito|OttieniRows) (Utility|Operatori|Aggiungi (Utility|Operatori|Moltiplica R 6) 3)) 10.0))
    (:then
      (Variabili|Predefinito|ImpostaSAct (Utilità|Stringa|Append (Utilità|Stringa|Append (Variabili|Predefinito|OttieniSCmd) " ") (Utilità|Stringa|ToString(Integer) (Matematica|Float|Truncate (Utilità|Array|Ottieni(unacopia) (Variabili|Predefinito|OttieniRows) (Utility|Operatori|Aggiungi (Utility|Operatori|Moltiplica R 6) 4)))))))
    (:else
        (Utilities|FlowControl|ForLoop :FirstIndex 0 :LastIndex (Utility|Operatori|Sottrai (Utilità|Array|Length (Variabili|Predefinito|OttieniTalNames)) 1)
    (:LoopBody
      (Funzionedichiamata|MatchAct :R R :K _index))))))
