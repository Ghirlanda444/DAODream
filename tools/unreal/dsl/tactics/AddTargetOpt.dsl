(fn AddTargetOpt (K)
  (Utilità|ControlloDiFlusso|Ramo (Utility|Operatori|Uguale(==) (Utilità|Array|Ottieni(unacopia) (Variabili|Predefinito|OttieniTTargets) (Utility|Operatori|Moltiplica K 2)) 6.0)
    (:then
        (Utilities|FlowControl|ForLoop :FirstIndex 0 :LastIndex (Utility|Operatori|Sottrai (Utilità|Array|Length (Variabili|Predefinito|OttieniMembers)) 1)
    (:LoopBody
      (Funzionedichiamata|AddMemberOpt :K _index))))
    (:else
      (Utilità|Array|Add (Variabili|Predefinito|OttieniOptIds) (Matematica|Float|Truncate (Utilità|Array|Ottieni(unacopia) (Variabili|Predefinito|OttieniTTargets) (Utility|Operatori|Moltiplica K 2))))
      (Utilità|Array|Add (Variabili|Predefinito|OttieniOptNames) (Utilità|Array|Ottieni(unacopia) (Variabili|Predefinito|OttieniTTargetNames) K)))))
