(fn LoadRows ()
  (Utilità|ControlloDiFlusso|Ramo (Utility|Operatori|Uguale(==) (Variabili|Predefinito|OttieniMemberIdx) 0)
    (:then
      (Variabili|Predefinito|ImpostaRows (Classe|BPPlotManager|OttieniPTactics (Variabili|Predefinito|OttieniMgr)))
      (Variabili|Predefinito|ImpostaSlots (Classe|BPPlotManager|OttieniPSlots (Variabili|Predefinito|OttieniMgr))))
    (:else
      (Variabili|Predefinito|ImpostaRows (Classe|BPDlgNPC|OttieniNTactics (Utilità|Array|Ottieni(unacopia) (Variabili|Predefinito|OttieniMembers) (Utility|Operatori|Sottrai (Variabili|Predefinito|OttieniMemberIdx) 1))))
      (Variabili|Predefinito|ImpostaSlots (Classe|BPDlgNPC|OttieniTacticSlots (Utilità|Array|Ottieni(unacopia) (Variabili|Predefinito|OttieniMembers) (Utility|Operatori|Sottrai (Variabili|Predefinito|OttieniMemberIdx) 1)))))))
