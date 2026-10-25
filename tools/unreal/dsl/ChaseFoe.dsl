(fn ChaseFoe (Dt)
  (bind (_fx _fy _fz) (Matematica|Vettore|BreakVector (Trasformazione|GetActorLocation (Variabili|Predefinito|OttieniFoe))))
  (bind (_sx _sy _sz) (Matematica|Vettore|BreakVector (Trasformazione|GetActorLocation (Variabili|Ottieniunriferimentoasestesso))))
  (Funzionedichiamata|FollowPath :Goal (Matematica|Vettore|MakeVector _fx _fy _sz) :Speed (Matematica|Float|SelectFloat 0.0 (Matematica|Float|SelectFloat 150.0 300.0 (Utility|Operatori|Maggiore(>) (Variabili|Predefinito|OttieniSlowUntil) (Utilità|Testo|GetGameTimeinSeconds))) (Utility|Operatori|Maggiore(>) (Variabili|Predefinito|OttieniRootUntil) (Utilità|Testo|GetGameTimeinSeconds))) :Dt Dt :bJog "true"))
