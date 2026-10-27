(fn SetBehOf ()
  (Utilità|ControlloDiFlusso|Ramo (Utility|Operatori|Uguale(==) (Variabili|Predefinito|OttieniMemberIdx) 0)
    (:then
      (Classe|BPPlotManager|SetPBehavior (Variabili|Predefinito|OttieniMgr) :B (Variabili|Predefinito|OttieniMBeh)))
    (:else
      (Classe|BPDlgNPC|SetBehavior (Utilità|Array|Ottieni(unacopia) (Variabili|Predefinito|OttieniMembers) (Utility|Operatori|Sottrai (Variabili|Predefinito|OttieniMemberIdx) 1)) :B (Variabili|Predefinito|OttieniMBeh)))))
