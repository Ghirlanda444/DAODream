(fn RegenAll ()
  (Utilità|ControlloDiFlusso|Ramo (Matematica|Booleano|ORBoolean (Variabili|Predefinito|OttieniPlayerDown) (Variabili|Predefinito|OttieniGameOver))
    (:else
      (Variabili|Predefinito|ImpostaPlayerHealth (Matematica|Float|Min(Float) (Utility|Operatori|Aggiungi (Variabili|Predefinito|OttieniPlayerHealth) 5.0) (Variabili|Predefinito|OttieniPlayerMaxHealth)))
      (Funzionedichiamata|ShowHealth)
      (bind _all (Attore|GetAllActorsOfClass "/Game/Cousland/Dialogue/BP_DlgNPC.BP_DlgNPC_C"))
      (for _a _all
        (Classe|BPDlgNPC|Regen _a :Amount 5.0)))))
