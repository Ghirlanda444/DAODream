(fn Recenter ()
  (Variabili|Predefinito|ImpostaPanOffset (Matematica|Vettore|MakeVector 0.0 0.0 0.0))
  (Classe|SpringArmComponent|ImpostaTargetOffset :self (Attore|GetComponentbyClass (Gioco|GetPlayerPawn 0) "/Script/Engine.SpringArmComponent") :TargetOffset (Matematica|Vettore|MakeVector 0.0 0.0 0.0)))
