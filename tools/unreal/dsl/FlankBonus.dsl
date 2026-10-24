(fn FlankBonus (Attacker Target Most)
  (Variabili|Predefinito|ImpostaLastFlank (Matematica|Float|MapRangeClamped (Matematica|Trig|Acos(Degrees) (Trasformazione|GetHorizontalDotProductTo Target Attacker)) 120.0 180.0 0.0 Most)))
