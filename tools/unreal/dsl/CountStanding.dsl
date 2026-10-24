(fn CountStanding ()
  (Variabili|Predefinito|ImpostaStanding 0)
  (bind _all (Attore|GetAllActorsOfClass "/Game/Cousland/Dialogue/BP_DlgNPC.BP_DlgNPC_C"))
  (for _a _all
    (Utilità|ControlloDiFlusso|Ramo (Matematica|Booleano|ANDBoolean (Classe|BPDlgNPC|OttieniInParty _a) (Matematica|Booleano|NOTBoolean (Classe|BPDlgNPC|OttieniDead _a)))
      (:then
        (Variabili|Predefinito|ImpostaStanding (Utility|Operatori|Aggiungi (Variabili|Predefinito|OttieniStanding) 1))))))
