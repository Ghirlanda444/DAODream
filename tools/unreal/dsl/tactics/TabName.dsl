(fn TabName (K)
  (Utilità|ControlloDiFlusso|Ramo (Utility|Operatori|Uguale(==) K 0)
    (:then
      (Variabili|Predefinito|ImpostaMName "Hero"))
    (:else
      (Variabili|Predefinito|ImpostaMName (Classe|BPDlgNPC|OttieniDisplayName (Utilità|Array|Ottieni(unacopia) (Variabili|Predefinito|OttieniMembers) (Utility|Operatori|Sottrai K 1)))))))
