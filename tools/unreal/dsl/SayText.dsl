(fn SayText (Txt)
  (bind _t (Gioco|Generaattoredallaclasse :Class "/Game/Cousland/Combat/BP_FloatText.BP_FloatText_C" :SpawnTransform (Matematica|Trasforma|MakeTransform (Utility|Operatori|Aggiungi (Trasformazione|GetActorLocation (Variabili|Ottieniunriferimentoasestesso)) (Matematica|Vettore|MakeVector 0.0 0.0 150.0)))))
  (Classe|BPFloatText|SetLabel _t :Txt Txt))
