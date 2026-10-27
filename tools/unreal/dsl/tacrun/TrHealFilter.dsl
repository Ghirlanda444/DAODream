(fn TrHealFilter ()
  (Utilità|ControlloDiFlusso|Ramo (Matematica|Booleano|ANDBoolean (Utility|Operatori|Uguale(==) (Variabili|Predefinito|OttieniTC) 4.0) (Utility|Operatori|Uguale(==) (Variabili|Predefinito|OttieniTS) 10104.0))
    (:then
      (Utilità|Array|Clear (Variabili|Predefinito|OttieniCL2))
  (Utilities|FlowControl|ForLoop :FirstIndex 0 :LastIndex (Utility|Operatori|Sottrai (Utilità|Array|Length (Variabili|Predefinito|OttieniCL)) 1)
    (:LoopBody
      (Funzionedichiamata|TrWound :K _index))
    (:Completed
      (Variabili|Predefinito|ImpostaCL (Variabili|Predefinito|OttieniCL2)))))))
