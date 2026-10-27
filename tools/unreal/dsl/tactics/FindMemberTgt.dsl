(fn FindMemberTgt (R)
  (Utilità|ControlloDiFlusso|Ramo (Matematica|Booleano|ANDBoolean (Utility|Operatori|Maggiore(>) (Utilità|Array|Ottieni(unacopia) (Variabili|Predefinito|OttieniRows) (Utility|Operatori|Aggiungi (Utility|Operatori|Moltiplica R 6) 5)) 0.0) (Utility|Operatori|Maggioreuguale(>=) (Utilità|Array|Ottieni(unacopia) (Variabili|Predefinito|OttieniRows) (Utility|Operatori|Aggiungi (Utility|Operatori|Moltiplica R 6) 0)) 100.0))
    (:then
        (Utilities|FlowControl|ForLoop :FirstIndex 0 :LastIndex (Utility|Operatori|Sottrai (Utilità|Array|Length (Variabili|Predefinito|OttieniMembers)) 1)
    (:LoopBody
      (Funzionedichiamata|MatchMemberTgt :R R :K _index))))))
