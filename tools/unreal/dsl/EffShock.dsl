(fn EffShock (K)
  (Funzionedichiamata|FaceToward :Goal (Trasformazione|GetActorLocation (Variabili|Predefinito|OttieniFoe)))
  (bind _all (Attore|GetAllActorsOfClass "/Game/Cousland/Dialogue/BP_DlgNPC.BP_DlgNPC_C"))
  (for _a _all
    (Funzionedichiamata|ShockHit _a :From (Variabili|Ottieniunriferimentoasestesso) :bPartySide (Variabili|Predefinito|OttieniInParty) :Amount (Utility|Operatori|Moltiplica (Utility|Operatori|Aggiungi (Variabili|Predefinito|OttieniSpellPower) 100.0) (Utilità|Array|Ottieni(unacopia) (Variabili|Predefinito|OttieniNTalents) (Utility|Operatori|Aggiungi (Utility|Operatori|Moltiplica K 18) 15)))))
  (Funzionedichiamata|SayText :Txt "Shock")
  (Utilità|ControlloDiFlusso|Ramo (Matematica|Booleano|ANDBoolean (Matematica|Booleano|NOTBoolean (Variabili|Predefinito|OttieniInParty)) (Matematica|Booleano|ANDBoolean (Utility|Operatori|Minore(<) (Trasformazione|GetDistanceTo (Variabili|Ottieniunriferimentoasestesso) (Gioco|GetPlayerPawn 0)) 1000.0) (Utility|Operatori|Maggioreuguale(>=) (Trasformazione|GetHorizontalDotProductTo (Variabili|Ottieniunriferimentoasestesso) (Gioco|GetPlayerPawn 0)) 0.819)))
    (:then
      (Classe|BPPlotManager|SpellHitPlayer (Variabili|Predefinito|OttieniMgr) :Amount (Utility|Operatori|Moltiplica (Utility|Operatori|Aggiungi (Variabili|Predefinito|OttieniSpellPower) 100.0) (Utilità|Array|Ottieni(unacopia) (Variabili|Predefinito|OttieniNTalents) (Utility|Operatori|Aggiungi (Utility|Operatori|Moltiplica K 18) 15)))))))
