(fn BowAttack ()
  (Variabili|Predefinito|ImpostaBestDist (Matematica|Float|Min(Float) (Utility|Operatori|Moltiplica (Variabili|Predefinito|OttieniBowRange) 100.0) 1500.0))
  (Variabili|Predefinito|ImpostaBestTarget)
  (bind _all (Attore|GetAllActorsOfClass "/Game/Cousland/Dialogue/BP_DlgNPC.BP_DlgNPC_C"))
  (for _a _all
    (Funzionedichiamata|TalentBid :Npc _a))
  (Funzionedichiamata|PreferTarget :Reach (Matematica|Float|Min(Float) (Utility|Operatori|Moltiplica (Variabili|Predefinito|OttieniBowRange) 100.0) 1500.0))
  (Utilità|ControlloDiFlusso|Ramo (Utilità|IsValid (Variabili|Predefinito|OttieniBestTarget))
    (:then
      (bind _arrow (Gioco|Generaattoredallaclasse :Class "/Game/Cousland/Combat/BP_Arrow.BP_Arrow_C" :SpawnTransform (Matematica|Trasforma|MakeTransform (Utility|Operatori|Aggiungi (Trasformazione|GetActorLocation (Gioco|GetPlayerPawn 0)) (Matematica|Vettore|MakeVector 0.0 0.0 140.0)))))
      (Classe|BPArrow|Launch _arrow :From (Utility|Operatori|Aggiungi (Trasformazione|GetActorLocation (Gioco|GetPlayerPawn 0)) (Matematica|Vettore|MakeVector 0.0 0.0 140.0)) :To (Utility|Operatori|Aggiungi (Trasformazione|GetActorLocation (Variabili|Predefinito|OttieniBestTarget)) (Matematica|Vettore|MakeVector 0.0 0.0 110.0)))
      (Classe|BPDlgNPC|TakeAttack (Variabili|Predefinito|OttieniBestTarget)))
    (:else
      (Funzionedichiamata|ShowMsg :Txt "No target in range"))))
