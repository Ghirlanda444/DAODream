(fn TrFolOne (A Idx)
  (Utilità|ControlloDiFlusso|Ramo (Matematica|Booleano|ANDBoolean (Matematica|Booleano|ANDBoolean (Utility|Operatori|Uguale(==) (Classe|BPDlgNPC|OttieniNIndex A) Idx) (Classe|BPDlgNPC|OttieniInParty A)) (Matematica|Booleano|NOTBoolean (Classe|BPDlgNPC|OttieniDead A)))
    (:then
      (Utilità|Array|Add (Variabili|Predefinito|OttieniCL) A))))
