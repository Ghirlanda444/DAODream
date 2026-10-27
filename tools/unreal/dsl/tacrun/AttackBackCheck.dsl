(fn AttackBackCheck ()
  (Funzionedichiamata|NFlag :Fl 7)
  (Utilità|ControlloDiFlusso|Ramo (Matematica|Booleano|ANDBoolean (Matematica|Booleano|NOTBoolean (Variabili|Predefinito|OttieniBFlag)) (Matematica|Booleano|NOTBoolean (Utilità|IsValid (Variabili|Predefinito|OttieniTarget))))
    (:then
      (Funzionedichiamata|NFlag :Fl 0)
  (Utilità|ControlloDiFlusso|Ramo (Variabili|Predefinito|OttieniBFlag)
    (:then
      (Variabili|Predefinito|ImpostaTacWho)
  (Utilities|FlowControl|ForLoop :FirstIndex 0 :LastIndex (Utility|Operatori|Sottrai (Utilità|Array|Length (Classe|BPPlotManager|OttieniEnL (Variabili|Predefinito|OttieniMgr))) 1)
    (:LoopBody
      (Funzionedichiamata|BackOne :K _index))
    (:Completed
  (Utilità|ControlloDiFlusso|Ramo (Utilità|IsValid (Variabili|Predefinito|OttieniTacWho))
    (:then
      (Funzionedichiamata|TacSetTarget))))))))))
