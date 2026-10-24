(fn ChaseFoe (Dt)
  (bind (_fx _fy _fz) (Matematica|Vettore|BreakVector (Trasformazione|GetActorLocation (Variabili|Predefinito|OttieniFoe))))
  (bind (_sx _sy _sz) (Matematica|Vettore|BreakVector (Trasformazione|GetActorLocation (Variabili|Ottieniunriferimentoasestesso))))
  (Funzionedichiamata|FollowPath :Goal (Matematica|Vettore|MakeVector _fx _fy _sz) :Speed 300.0 :Dt Dt :bJog "true"))
