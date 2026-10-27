(fn AddCmdKind (K)
  (Utilità|ControlloDiFlusso|Ramo (Matematica|Booleano|ORBoolean (Utility|Operatori|Uguale(==) (Variabili|Predefinito|OttieniCmdId) 2.0) (Utility|Operatori|Uguale(==) (Variabili|Predefinito|OttieniCmdId) 3.0))
    (:then
      (Funzionedichiamata|AddOpt :Name (Utilità|Array|Ottieni(unacopia) (Variabili|Predefinito|OttieniTCmdNames) K) :Cmd (Variabili|Predefinito|OttieniCmdId) :Sub 0.0))
    (:else
        (Utilità|ControlloDiFlusso|Ramo (Matematica|Booleano|ORBoolean (Matematica|Booleano|ORBoolean (Utility|Operatori|Uguale(==) (Variabili|Predefinito|OttieniCmdId) 4.0) (Utility|Operatori|Uguale(==) (Variabili|Predefinito|OttieniCmdId) 5.0)) (Utility|Operatori|Uguale(==) (Variabili|Predefinito|OttieniCmdId) 6.0))
    (:then
        (Utilities|FlowControl|ForLoop :FirstIndex 0 :LastIndex (Utility|Operatori|Sottrai (Utilità|Array|Length (Variabili|Predefinito|OttieniTalNames)) 1)
    (:LoopBody
      (Funzionedichiamata|AddTalOpt :K _index))))
    (:else
        (Utilità|ControlloDiFlusso|Ramo (Utility|Operatori|Uguale(==) (Variabili|Predefinito|OttieniCmdId) 10.0)
    (:then
      (Variabili|Predefinito|ImpostaJumpName (Utilità|Array|Ottieni(unacopia) (Variabili|Predefinito|OttieniTCmdNames) K))
        (Utilities|FlowControl|ForLoop :FirstIndex 0 :LastIndex (Utility|Operatori|Sottrai (Variabili|Predefinito|OttieniSlots) 1)
    (:LoopBody
      (Funzionedichiamata|AddJumpOpt :K _index))))
    (:else
        (Utilità|ControlloDiFlusso|Ramo (Utility|Operatori|Uguale(==) (Variabili|Predefinito|OttieniMemberIdx) 0)
    (:then
      (Funzionedichiamata|AddOpt :Name (Utilità|Array|Ottieni(unacopia) (Variabili|Predefinito|OttieniTCmdNames) K) :Cmd (Variabili|Predefinito|OttieniCmdId) :Sub 0.0))))))))))
