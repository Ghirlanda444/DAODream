(fn ShootFx ()
  (Utilità|ControlloDiFlusso|Ramo (Matematica|Booleano|ANDBoolean (Utility|Operatori|Maggiore(>) (Variabili|Predefinito|OttieniNRange) 0.0) (Utilità|IsValid (Variabili|Predefinito|OttieniFoe)))
    (:then
      (bind _a (Gioco|Generaattoredallaclasse :Class "/Game/Cousland/Combat/BP_Arrow.BP_Arrow_C" :SpawnTransform (Matematica|Trasforma|MakeTransform (Utility|Operatori|Aggiungi (Trasformazione|GetActorLocation (Variabili|Ottieniunriferimentoasestesso)) (Matematica|Vettore|MakeVector 0.0 0.0 140.0)))))
      (Classe|BPArrow|Launch _a :From (Utility|Operatori|Aggiungi (Trasformazione|GetActorLocation (Variabili|Ottieniunriferimentoasestesso)) (Matematica|Vettore|MakeVector 0.0 0.0 140.0)) :To (Utility|Operatori|Aggiungi (Trasformazione|GetActorLocation (Variabili|Predefinito|OttieniFoe)) (Matematica|Vettore|MakeVector 0.0 0.0 110.0))))))
