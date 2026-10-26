(fn Commit ()
  (Utilità|ControlloDiFlusso|Ramo (Utility|Operatori|Uguale(==) (Variabili|Predefinito|OttieniMemberIdx) 0)
    (:then
      (Classe|BPPlotManager|SetPlayerTactics (Variabili|Predefinito|OttieniMgr) :InTactics (Variabili|Predefinito|OttieniRows)))
    (:else
      (Classe|BPDlgNPC|SetTacticRows (Utilità|Array|Ottieni(unacopia) (Variabili|Predefinito|OttieniMembers) (Utility|Operatori|Sottrai (Variabili|Predefinito|OttieniMemberIdx) 1)) :InRows (Variabili|Predefinito|OttieniRows)))))
