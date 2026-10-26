(fn EffMindBlast (K)
  (bind _all (Attore|GetAllActorsOfClass "/Game/Cousland/Dialogue/BP_DlgNPC.BP_DlgNPC_C"))
  (for _a _all
    (Funzionedichiamata|BlastHit _a :From (Variabili|Ottieniunriferimentoasestesso) :bPartySide (Variabili|Predefinito|OttieniInParty) :Seconds (Utilità|Array|Ottieni(unacopia) (Variabili|Predefinito|OttieniNTalents) (Utility|Operatori|Aggiungi (Utility|Operatori|Moltiplica K 18) 7))))
  (Funzionedichiamata|SayText :Txt "Mind Blast")
  (Utilità|ControlloDiFlusso|Ramo (Matematica|Booleano|ANDBoolean (Matematica|Booleano|NOTBoolean (Variabili|Predefinito|OttieniInParty)) (Utility|Operatori|Minore(<) (Trasformazione|GetDistanceTo (Variabili|Ottieniunriferimentoasestesso) (Gioco|GetPlayerPawn 0)) 500.0))
    (:then
      (Classe|BPPlotManager|StunPlayer (Variabili|Predefinito|OttieniMgr) :Seconds (Utility|Operatori|Moltiplica (Utilità|Array|Ottieni(unacopia) (Variabili|Predefinito|OttieniNTalents) (Utility|Operatori|Aggiungi (Utility|Operatori|Moltiplica K 18) 7)) 0.8) :bFall "false"))))
