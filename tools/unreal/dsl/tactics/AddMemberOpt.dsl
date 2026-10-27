(fn AddMemberOpt (K)
  (Utilità|ControlloDiFlusso|Ramo (Utility|Operatori|Uguale(==) K (Utility|Operatori|Sottrai (Variabili|Predefinito|OttieniMemberIdx) 1))
    (:else
      (Utilità|Array|Add (Variabili|Predefinito|OttieniOptIds) (Utility|Operatori|Aggiungi (Classe|BPDlgNPC|OttieniNIndex (Utilità|Array|Ottieni(unacopia) (Variabili|Predefinito|OttieniMembers) K)) 100))
      (Utilità|Array|Add (Variabili|Predefinito|OttieniOptNames) (Classe|BPDlgNPC|OttieniDisplayName (Utilità|Array|Ottieni(unacopia) (Variabili|Predefinito|OttieniMembers) K))))))
