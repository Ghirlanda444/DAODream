(fn BackAway (From)
  (bind (_x _y _z) (Matematica|Vettore|BreakVector (Utility|Operatori|Sottrai (Trasformazione|GetActorLocation (Variabili|Ottieniunriferimentoasestesso)) (Trasformazione|GetActorLocation From))))
  (Variabili|Predefinito|ImpostaFleeGoal (Utility|Operatori|Aggiungi (Trasformazione|GetActorLocation (Variabili|Ottieniunriferimentoasestesso)) (Utility|Operatori|Moltiplica (Matematica|Vettore|Normalize (Matematica|Vettore|MakeVector _x _y 0.0)) (Matematica|Vettore|MakeVector 500.0 500.0 0.0))))
  (Variabili|Predefinito|ImpostaFleeUntil (Utility|Operatori|Aggiungi (Utilità|Testo|GetGameTimeinSeconds) 1.5)))
